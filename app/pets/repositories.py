from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.pets.models import Pet, PetAttachment
from app.pets.schemas import SPetListParams


class PetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _build_filtered_pets_query(
        self,
        params: SPetListParams,
        *,
        owner_id: int | None = None,
    ):
        statement = select(Pet)

        if owner_id is not None:
            statement = statement.where(Pet.owner_id == owner_id)
        if params.search:
            pattern = f"%{params.search}%"
            statement = statement.where(
                or_(
                    Pet.name.ilike(pattern),
                    Pet.breed.ilike(pattern),
                    Pet.description.ilike(pattern),
                    Pet.address.ilike(pattern),
                    Pet.chip_number.ilike(pattern),
                    Pet.brand_number.ilike(pattern),
                )
            )
        if params.type:
            statement = statement.where(func.lower(Pet.type) == params.type)
        if params.status:
            statement = statement.where(Pet.status == params.status.value)
        if params.sex:
            statement = statement.where(func.lower(Pet.sex) == params.sex)
        if params.color:
            statement = statement.where(func.lower(Pet.color) == params.color)

        return statement

    def _build_order_by(self, params: SPetListParams) -> list:
        direction = asc if params.sort_order == "asc" else desc

        if params.sort_by == "found_date":
            return [
                direction(Pet.found_date),
                direction(Pet.found_time),
                desc(Pet.id),
            ]
        if params.sort_by == "name":
            return [direction(func.lower(Pet.name)).nullslast(), desc(Pet.id)]
        if params.sort_by == "type":
            return [direction(func.lower(Pet.type)).nullslast(), desc(Pet.id)]
        if params.sort_by == "status":
            return [direction(Pet.status).nullslast(), desc(Pet.id)]
        return [direction(Pet.id)]

    async def list_filtered(
        self,
        params: SPetListParams,
        *,
        owner_id: int | None = None,
    ) -> tuple[list[Pet], int]:
        base_query = self._build_filtered_pets_query(params, owner_id=owner_id)
        total_result = await self.session.execute(
            select(func.count()).select_from(base_query.order_by(None).subquery())
        )
        total = int(total_result.scalar_one())

        items_result = await self.session.execute(
            base_query
            .order_by(*self._build_order_by(params))
            .offset((params.page - 1) * params.page_size)
            .limit(params.page_size)
        )
        return list(items_result.scalars().all()), total

    async def list_for_sitemap(self, limit: int = 5000) -> list[Pet]:
        result = await self.session.execute(select(Pet).order_by(desc(Pet.id)).limit(limit))
        return list(result.scalars().all())

    async def list_with_embeddings_by_type(self, pet_type: str) -> list[Pet]:
        result = await self.session.execute(
            select(Pet).where(Pet.type == pet_type, Pet.embedding.isnot(None))
        )
        return list(result.scalars().all())

    async def get_by_id(self, pet_id: int) -> Pet | None:
        result = await self.session.execute(select(Pet).where(Pet.id == pet_id))
        return result.scalar_one_or_none()

    async def create(self, pet_data: dict) -> Pet:
        pet = Pet(**pet_data)
        self.session.add(pet)
        await self.session.commit()
        await self.session.refresh(pet)
        return pet

    async def update(self, pet: Pet, pet_data: dict) -> Pet:
        for key, value in pet_data.items():
            setattr(pet, key, value)
        await self.session.commit()
        await self.session.refresh(pet)
        return pet

    async def delete(self, pet: Pet) -> None:
        await self.session.delete(pet)
        await self.session.commit()

    async def list_attachments(self, pet_id: int) -> list[PetAttachment]:
        result = await self.session.execute(
            select(PetAttachment)
            .where(PetAttachment.pet_id == pet_id)
            .order_by(desc(PetAttachment.created_at), desc(PetAttachment.id))
        )
        return list(result.scalars().all())

    async def get_attachment(self, pet_id: int, attachment_id: int) -> PetAttachment | None:
        result = await self.session.execute(
            select(PetAttachment).where(
                PetAttachment.pet_id == pet_id,
                PetAttachment.id == attachment_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_latest_image_attachment(self, pet_id: int) -> PetAttachment | None:
        result = await self.session.execute(
            select(PetAttachment)
            .where(
                PetAttachment.pet_id == pet_id,
                PetAttachment.is_image.is_(True),
            )
            .order_by(desc(PetAttachment.created_at), desc(PetAttachment.id))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create_attachment(self, attachment_data: dict) -> PetAttachment:
        attachment = PetAttachment(**attachment_data)
        self.session.add(attachment)
        await self.session.commit()
        await self.session.refresh(attachment)
        return attachment

    async def delete_attachment(self, attachment: PetAttachment) -> None:
        await self.session.delete(attachment)
        await self.session.commit()
