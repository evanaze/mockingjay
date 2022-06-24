"""Fine-tunes the model based on the dataset of tweets."""


class FineTune:
    def __init__(self, model_path: str) -> None:
        """Fine tunes the model.

        :param model_path: The actual path to the model to fine-tune
        """
        self.model_path = model_path
