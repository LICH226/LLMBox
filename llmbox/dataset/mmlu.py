from logging import getLogger

from .multiple_choice_dataset import MultipleChoiceDataset

logger = getLogger(__name__)


class Mmlu(MultipleChoiceDataset):
    """The dataset of MMLU.

    Measuring Massive Multitask Language Understanding by Dan Hendrycks, Collin Burns, Steven Basart, Andy Zou, Mantas Mazeika, Dawn Song, and Jacob Steinhardt (ICLR 2021).

    Example:
        "question": "What is the embryological origin of the hyoid bone?",
        "choices": ["The first pharyngeal arch", "The first and second pharyngeal arches", "The second pharyngeal arch", "The second and third pharyngeal arches"],
        "answer": 3
    """

    instruction = "The following are multiple choice questions (with answers) about {}."
    evaluation_set = "test"
    example_set = "dev"
    load_args = ("hails/mmlu_no_train",)  # remove "all" by default

    def __init__(self, args, model, subset_name: str):
        self.instruction = self.instruction.format(self._format_subject(subset_name))
        if args.ranking_type == "ppl_of_whole_option":
            self.source_prefix = "Question: "
        elif args.ranking_type == "prob_of_just_option":
            self.source_prefix = ""
        super().__init__(args, model, subset_name)

    @staticmethod
    def _format_subject(subject: str) -> str:
        return subject.replace("_", " ")

    def format_instance(self, instance):
        options = list(map(lambda op: " " + op, instance["choices"]))
        return dict(
            source=self.source_prefix + instance["question"].strip(),
            source_postfix="\nAnswer:",
            target_idx=instance["answer"],
            options=options,
        )

    def calculate_metric(self, predictions):
        results, score_lists = super().calculate_metric(predictions)
        return results, score_lists

    @property
    def references(self):
        return [instance["answer"] for instance in self.evaluation_data]
