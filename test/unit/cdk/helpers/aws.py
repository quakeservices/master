class AWSHelper:
    @staticmethod
    def format_id_for_aws(input_string: str) -> str:
        return input_string.replace(".", "-").replace("_", "-")

    @staticmethod
    def format_string_for_aws(input_string: str) -> str:
        return input_string.replace(".", "").replace("_", "-")
