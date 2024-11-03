import json

from app.models.subscription_data import subscription_data


class Config:
    def __init__(self, config_file, setting_file, subscription_file):
        self.bangumi_subscription = []
        self.config_file = config_file
        self.setting_file = setting_file
        self.subscription_file = subscription_file
        with open(setting_file, "r") as f:
            self.setting_data = json.load(f)

        self.my_domain = self.get_config("my_domain")
        self.use_domain = self.my_domain != ""
        self.mikan_episode = "https://mikanani.me/Home/Episode/"
        self.mikan_home = "https://mikanani.me/Home/Bangumi/"
        self.rss_url = self.get_config("mikan_rss_url")
        self.filters = self.get_config("filter_words").split(",")
        self.get_bangumi_moe_subscription()

    def get_config(self, key):
        """
        获取config文件的信息
        :param str key: 对应的key
        """
        with open(self.config_file, "r", encoding = "utf-8") as f:
            config_data = json.load(f)
        return config_data.get(key)

    def get_setting(self, key):
        """
        获取setting文件的信息
        :param str key: 对应的key
        """
        with open(self.setting_file, "r") as f:
            setting_data = json.load(f)
        return setting_data.get(key)

    def set_config(self, key, value):
        """
        修改config文件的信息
        :param str key: 要修改的key
        :param value: 要设置的新值
        """
        # 首先读取当前的配置数据
        with open(self.config_file, "r") as f:
            config_data = json.load(f)

        # 修改指定的键的值
        config_data[key] = value

        # 将修改后的数据写回到配置文件中
        with open(self.config_file, "w") as f:
            json.dump(
                    config_data, f, indent = 4
            )  # 使用indent参数使输出的JSON格式化，更易读

    def fresh_config(self):
        self.my_domain = self.get_config("my_domain")
        self.use_domain = self.my_domain != ""
        self.mikan_episode = "https://mikanani.me/Home/Episode/"
        self.mikan_home = "https://mikanani.me/Home/Bangumi/"
        self.rss_url = self.get_config("mikan_rss_url")
        self.filters = self.get_config("filter_words").split(",")

    def get_bangumi_moe_subscription(self):
        with open(self.subscription_file, "r", encoding = 'utf-8') as f:
            config_data = json.load(f)

        sub_dict = config_data.get("bangumi_moe")
        self.bangumi_subscription.clear()
        for sub_json in sub_dict:
            new_subscription = subscription_data(rss_url = sub_json.get("rss_url"),
                                                 subject_id = sub_json.get("subject_id"))
            self.bangumi_subscription.append(new_subscription)

    def get_temp_rss(self):
        with open(self.subscription_file, "r", encoding = 'utf-8') as f:
            config_data = json.load(f)
        temp_list = config_data.get("temp_mikan")
        return temp_list

    def renew_temp_rss(self, temp_list):
        with open(self.subscription_file, 'r', encoding = 'utf-8') as file:
            data = json.load(file)

            # 更新 temp_mikan
            data["temp_mikan"] = temp_list

        # 将更新后的 JSON 数据写回文件
        with open(self.subscription_file, 'w', encoding = 'utf-8') as file:
            json.dump(data, file, indent = 4, ensure_ascii = False)

    def clear_temp_rss(self):
        with open(self.subscription_file, 'r', encoding = 'utf-8') as file:
            data = json.load(file)

            # 更新 temp_mikan
            data["temp_mikan"] = []

        # 将更新后的 JSON 数据写回文件
        with open(self.subscription_file, 'w', encoding = 'utf-8') as file:
            json.dump(data, file, indent = 4, ensure_ascii = False)
