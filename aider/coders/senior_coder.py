from .ask_coder import AskCoder
from .base_coder import Coder
from .senior_prompts import SeniorPrompts


class SeniorCoder(AskCoder):
    edit_format = "senior"
    gpt_prompts = SeniorPrompts()

    def reply_completed(self):
        content = self.partial_response_content

        if not self.io.confirm_ask("Edit the files?"):
            return

        kwargs = dict()

        # Use the junior_model from the main_model if it exists, otherwise use the main_model itself
        junior_model = self.main_model.junior_model or self.main_model

        kwargs["main_model"] = junior_model
        kwargs["edit_format"] = self.main_model.junior_edit_format
        kwargs["suggest_shell_commands"] = False
        kwargs["map_tokens"] = 0
        kwargs["total_cost"] = self.total_cost
        kwargs["cache_prompts"] = False
        kwargs["num_cache_warming_pings"] = 0

        new_kwargs = dict(io=self.io, from_coder=self)
        new_kwargs.update(kwargs)

        junior_coder = Coder.create(**new_kwargs)
        junior_coder.cur_messages = []
        junior_coder.done_messages = []
        junior_coder.show_announcements()

        junior_coder.run(with_message=content, preproc=False)

        self.move_back_cur_messages("I made those changes to the files.")
        self.total_cost = junior_coder.total_cost
