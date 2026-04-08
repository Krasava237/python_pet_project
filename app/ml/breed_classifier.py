import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image

class DogBreedClassifier:
    def __init__(self):
        model_name = "dima806/133_dog_breeds_image_detection"

        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = AutoModelForImageClassification.from_pretrained(model_name)
        self.model.eval()

        self.id2label = self.model.config.id2label

    def predict(self, image_path: str):
        img = Image.open(image_path).convert("RGB")
        inputs = self.processor(images=img, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits

        probs = logits.softmax(dim=1).squeeze()
        conf, class_id = torch.max(probs, dim=0)

        breed = self.id2label[class_id.item()]
        confidence = float(conf.item())

        return {
            "breed": breed.replace("_", " ").title(),
            "confidence": round(confidence, 4)
        }

dog_breed_model = DogBreedClassifier()
