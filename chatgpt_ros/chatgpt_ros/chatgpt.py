import requests


class ChatGPT:
    def __init__(self, api_key: str) -> None:
        """
        Constructer

        Parameters
        ----------
        api_key : str
            API key for OpenAI
        """
        self.api_key: str = api_key
        self.endpoint: str = "https://api.openai.com/v1/chat/completions"

        self.role_system: dict = {"role": "system", "content": None}
        self.past_content_list: list = []
        self.num_hold_pass_res: int = 0
        self.set_past: bool = False
        self.set_system: bool = False

    def set_past_content(self, u_content: str, a_content: str) -> None:
        """
        Set the assistant content of message for the ChatGPT API.
        Parameters
        ----------
        u_content : str
            The prompt of the message to set for the past prompt.
        a_content : str
            The content of the message to set for the assistant.
        """
        assistant: dict = {"role": "assistant", "content": a_content}
        prompt: dict = {"role": "user", "content": u_content}
        self.past_content_list.append(prompt)
        self.past_content_list.append(assistant)
        diff_num: int = len(self.past_content_list) / 2 - self.num_hold_pass_res
        if diff_num > 0:
            for _ in range(int(diff_num)):
                self.past_content_list.pop(0)
        self.set_past = True

    def set_system_content(self, content):
        """
        Set the system content of message for the ChatGPT API.

        Parameters
        ----------
        content : str
            The content of the message to set for the system.
        """
        self.role_system["content"] = content
        self.set_system = True

    def generate_text(self, prompt: str, length: int = 50) -> str:
        """
        Generates text response from ChatGPT API given a prompt.

        Parameters
        ----------
        prompt : str
            The prompt message to initiate the conversation with ChatGPT API.

        length : int, optional
            The maximum number of tokens to generate in the response message.
            Default is 50.

        Returns
        -------
        str
            The generated response text from ChatGPT API.

        Raises
        ------
        requests.exceptions.HTTPError
            If the request to ChatGPT API returns an error status code.
        """
        intermediate_prompt = ''' You are a robot command generator. Our robot is a home robot that can move in any direction, pick up and drop off objects, and detect obstacles in its path. To generate a command, please provide a prompt in spoken language, like "I need a coffee". We will use OpenAI to convert your prompt into a command in JSON format that best fits the meaning. Currently our home have four tables, Table 1 have coke can and coffee powder, Table 2 have a coffee mug, Table 3 have Water bottle, and Table 4 have kettle.  The structure of the command should be: {Objects", "params": {"Object1": "Coffee Mug", "Object2": "Water Bottle", "Object3": "Kettle", "Object4":"Coffee Powder"} Actions", "params":{"Action1": "Move", "Action2": "Pick", "Action3": "Move", "Action4":"Pick", "Action5": "Move", "Action6":"Pick", "Action7": "Move", "Action8":"Pick"} Locations", "params":{"Location1": "Table 2", "Location2": "Table 3", "Location3": "Table 3", "Location4": "Table 1"}}. If I ask something like food you should give instructions to prepare it and bring it back to the user not just taking and bringing it back to the user. For things which cannot be made in home, you can just pickup and bring it back to the user.'''
        final_prompt = intermediate_prompt + prompt
        messages: list[dict] = []
        if self.set_system:
            messages.append(self.role_system)
        if self.set_past:
            for past in self.past_content_list:
                messages.append(past)
        messages.append({"role": "user", "content": final_prompt})
        headers: dict = {   
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload: dict = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "max_tokens": length,
            "temperature": 0.5,
            "n": 1,
            "stop": ".",
        }
        print("message : ", messages)
        try:
            response = requests.post(
                self.endpoint, headers=headers, json=payload, timeout=(3.0, 7.5)
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print("HTTP Error!", e)
            result_content = str(e)
        else:
            result: dict = response.json()
            print("result  : ", result)
            result_content: str = result["choices"][0]["message"]["content"]
            self.set_past_content(prompt, result_content)
        return result_content
