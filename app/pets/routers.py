import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import RedirectResponse

from app.integrations.nominatim import NominatimService
from app.pets.dependencies import (
    get_nominatim_service,
    get_pet_list_params,
    get_pet_service,
    require_pet_access,
)
from app.pets.schemas import (
    SPaginatedPetsResponse,
    SPetAttachmentDownloadResponse,
    SPetAttachmentResponse,
    SPetCreate,
    SPetListParams,
    SPetLocationInsightResponse,
    SPetResponse,
    SPetUpdate,
)
from app.pets.services import PetService
from app.security import Permission
from app.storage.service import StorageUnavailableError
from app.users.dependencies import get_current_user, require_permission
from app.users.models import User
from app.utils.files import ensure_media_dir, secure_filename, validate_image_and_save

router = APIRouter(prefix="/pets", tags=["Pets"])


def _get_image_to_embedding():
    try:
        from app.ml.embeddings import image_to_embedding

        return image_to_embedding
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Image embedding model is unavailable: {exc}",
        ) from exc


def _get_breed_model():
    try:
        from app.ml.breed_classifier import dog_breed_model

        return dog_breed_model
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Breed classification model is unavailable: {exc}",
        ) from exc


def _raise_storage_error(exc: StorageUnavailableError) -> None:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=str(exc),
    ) from exc


@router.get("/", response_model=SPaginatedPetsResponse)
async def get_pets(
    params: SPetListParams = Depends(get_pet_list_params),
    pet_service: PetService = Depends(get_pet_service),
):
    return await pet_service.list_pets(params)


@router.get("/my", response_model=SPaginatedPetsResponse)
async def get_my_pets(
    params: SPetListParams = Depends(get_pet_list_params),
    current_user: User = Depends(require_permission(Permission.PETS_READ)),
    pet_service: PetService = Depends(get_pet_service),
):
    return await pet_service.find_by_owner(current_user.id, params)


@router.get("/{pet_id}/photo")
async def get_pet_photo(pet_id: int, pet_service: PetService = Depends(get_pet_service)):
    pet = await pet_service.get_by_id(pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    photo_url = await pet_service.get_photo_redirect_url(pet)
    if not photo_url:
        raise HTTPException(status_code=404, detail="Photo not found")

    return RedirectResponse(url=photo_url)


@router.get("/{pet_id}", response_model=SPetResponse)
async def get_pet(pet_id: int, pet_service: PetService = Depends(get_pet_service)):
    pet = await pet_service.get_public_by_id(pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    return pet


@router.get("/{pet_id}/location-insight", response_model=SPetLocationInsightResponse)
async def get_pet_location_insight(
    pet_id: int,
    pet_service: PetService = Depends(get_pet_service),
    nominatim_service: NominatimService = Depends(get_nominatim_service),
):
    pet = await pet_service.get_by_id(pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    return await nominatim_service.lookup_address(pet.address)


@router.post("/", response_model=SPetResponse, status_code=201)
async def create_pet(
    pet: SPetCreate,
    current_user: User = Depends(require_permission(Permission.PETS_CREATE)),
    pet_service: PetService = Depends(get_pet_service),
):
    payload = pet.model_dump()
    payload["owner_id"] = current_user.id
    return await pet_service.create_pet(payload)


@router.put("/{pet_id}", response_model=SPetResponse)
async def update_pet(
    pet_update: SPetUpdate,
    pet=Depends(require_pet_access(Permission.PETS_UPDATE_OWN)),
    pet_service: PetService = Depends(get_pet_service),
):
    update_data = pet_update.model_dump(exclude_unset=True)
    return await pet_service.update_pet(pet, update_data)


@router.get("/{pet_id}/attachments", response_model=list[SPetAttachmentResponse])
async def list_pet_attachments(
    pet=Depends(require_pet_access(Permission.PETS_ATTACHMENTS_READ_OWN)),
    pet_service: PetService = Depends(get_pet_service),
):
    return await pet_service.list_attachments(pet.id)


@router.post(
    "/{pet_id}/attachments",
    response_model=SPetAttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_pet_attachment(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    pet=Depends(require_pet_access(Permission.PETS_ATTACHMENTS_WRITE_OWN)),
    pet_service: PetService = Depends(get_pet_service),
):
    try:
        return await pet_service.upload_attachment(
            pet,
            uploaded_by_id=current_user.id,
            file=file,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except StorageUnavailableError as exc:
        _raise_storage_error(exc)


@router.get(
    "/{pet_id}/attachments/{attachment_id}/download-url",
    response_model=SPetAttachmentDownloadResponse,
)
async def get_pet_attachment_download_url(
    attachment_id: int,
    pet=Depends(require_pet_access(Permission.PETS_ATTACHMENTS_READ_OWN)),
    pet_service: PetService = Depends(get_pet_service),
):
    try:
        return await pet_service.get_attachment_download_url(pet.id, attachment_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except StorageUnavailableError as exc:
        _raise_storage_error(exc)


@router.delete("/{pet_id}/attachments/{attachment_id}", status_code=status.HTTP_200_OK)
async def delete_pet_attachment(
    attachment_id: int,
    pet=Depends(require_pet_access(Permission.PETS_ATTACHMENTS_DELETE_OWN)),
    pet_service: PetService = Depends(get_pet_service),
):
    try:
        await pet_service.delete_attachment(pet.id, attachment_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except StorageUnavailableError as exc:
        _raise_storage_error(exc)
    return {"detail": "Attachment deleted"}


@router.delete("/{pet_id}", status_code=status.HTTP_200_OK)
async def delete_pet(
    pet=Depends(require_pet_access(Permission.PETS_DELETE_OWN)),
    pet_service: PetService = Depends(get_pet_service),
):
    try:
        await pet_service.delete_pet(pet)
    except StorageUnavailableError as exc:
        _raise_storage_error(exc)
    return {"detail": "Pet deleted"}


@router.post("/{pet_id}/upload_photo", response_model=SPetResponse)
async def upload_pet_photo(
    file: UploadFile = File(...),
    pet=Depends(require_pet_access(Permission.PETS_UPLOAD_PHOTO_OWN)),
    pet_service: PetService = Depends(get_pet_service),
):
    ensure_media_dir()

    fname = secure_filename(file.filename)
    dest = Path("media/pets") / str(pet.id)
    dest.mkdir(parents=True, exist_ok=True)
    file_path = dest / fname

    try:
        validate_image_and_save(file, file_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        file.file.close()

    image_to_embedding = _get_image_to_embedding()
    photo_url = f"/media/pets/{pet.id}/{fname}"
    try:
        emb = image_to_embedding(str(file_path))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error while processing image: {exc}",
        ) from exc

    return await pet_service.update_pet(pet, {"photo_url": photo_url, "embedding": emb})


@router.post("/find_similar")
async def find_similar_pets(
    type: str,
    file: UploadFile = File(...),
    pet_service: PetService = Depends(get_pet_service),
):
    image_to_embedding = _get_image_to_embedding()

    temp_path = Path("media/temp")
    temp_path.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix.lower()
    temp_file = temp_path / f"query{ext}"

    data = file.file.read()
    with open(temp_file, "wb") as temp_handle:
        temp_handle.write(data)
    file.file.close()

    try:
        query_emb = image_to_embedding(str(temp_file))
    except Exception as exc:
        temp_file.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error while processing image: {exc}",
        ) from exc

    result = await pet_service.find_similar_by_embedding(type, query_emb, top_k=5)
    temp_file.unlink(missing_ok=True)
    return result


@router.post("/predict_breed")
async def predict_breed(file: UploadFile = File(...)):
    dog_breed_model = _get_breed_model()

    with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        return dog_breed_model.predict(tmp_path)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Image processing failed: {exc}",
        ) from exc
