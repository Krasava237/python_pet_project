import torch
import torchvision.transforms as T
from torchvision import models
from PIL import Image
import numpy as np

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

_resnet = models.resnet50(pretrained=True)

modules = list(_resnet.children())[:-1]
feature_extractor = torch.nn.Sequential(*modules)
feature_extractor.to(device)
feature_extractor.eval()

_preprocess = T.Compose([
    T.Resize(256),
    T.CenterCrop(224),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]),
])


def image_to_embedding(image_path: str):
    """
    Принимает путь к изображению (str или Path), возвращает list[float] нормализованный (L2).
    """
    img = Image.open(image_path).convert("RGB")
    tensor = _preprocess(img).unsqueeze(0).to(device)
    with torch.no_grad():
        feats = feature_extractor(tensor)
    feats = feats.squeeze()
    arr = feats.cpu().numpy().astype(np.float32)

    norm = np.linalg.norm(arr)
    if norm > 0:
        arr = arr / norm
    return arr.tolist()
