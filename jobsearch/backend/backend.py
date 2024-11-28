from jobsearch.search.profile import Portfolio
from jobsearch.resumes.llm import LLM, LLMAPIOptions, Model

import gnupg
import configparser
import platform
import enum
import os
import json
import pickle
from pathlib import Path

from collections.abc import ItemsView

class ConfigurationElements(enum.Enum):
    save_dir = enum.auto()
    platform = enum.auto()
    API_Keys = enum.auto()
    gnupghome = enum.auto()
    gpgbinary = enum.auto()
    gpguser = enum.auto()
    llm_configs = enum.auto()

class Configuration(configparser.ConfigParser):
    FILENAME="config.ini"
    def __init__(
            self,
            directory="./jobs",
            user="",
            defaults=None,
            dict_type=configparser._default_dict,
            allow_no_value=False,
            *,
            delimiters=('=', ':'),
            comment_prefixes=('#', ';'),
            inline_comment_prefixes=None,
            strict=True,
            empty_lines_in_values=True,
            default_section=configparser.DEFAULTSECT,
            converters=configparser._UNSET,
            allow_unnamed_section=False,) -> None:
        super().__init__(
            defaults=defaults,
            dict_type=dict_type,
            allow_no_value=allow_no_value,
            delimiters=delimiters,
            comment_prefixes=comment_prefixes,
            inline_comment_prefixes=inline_comment_prefixes,
            strict=strict,
            empty_lines_in_values=empty_lines_in_values,
            default_section=default_section,
            interpolation=configparser.ExtendedInterpolation(),
            converters=converters,
            allow_unnamed_section=allow_unnamed_section,
        )
        directory = Path(directory)
        self.config_file = directory/Configuration.FILENAME
        self.user = user
        if self.config_file.exists():
            self.read(self.config_file)
        else:
            self.default_config()
        self.platform = platform.system()
    
    def default_config(self):
        self["DEFAULT"] = {
        ConfigurationElements.save_dir.name: str(self.config_file.parent.resolve()),
        ConfigurationElements.platform.name:platform.system(),
        ConfigurationElements.API_Keys.name: "${save_dir}/api_keys.txt.gpg",
        ConfigurationElements.llm_configs.name: "${save_dir}/llm_configs.json",
        ConfigurationElements.gpguser.name: self.user,
        }
        self['Linux'] = {
            ConfigurationElements.gnupghome.name: "${HOME}/.gnupg",
            ConfigurationElements.gpgbinary.name: "gpg",
        }
        self['Windows'] = {
            ConfigurationElements.gnupghome.name: "${APPDATA}\\gnupg",
            ConfigurationElements.gpgbinary.name: "C:\\Program Files (x86)\\gnupg\\bin\\gpg.exe",
        }

    def gett(
            self,
            option,
            *,
            raw=False,
            vars=None,
            fallback=configparser._UNSET):
        return self.get(
            self.platform,
            option,
            raw=raw,
            vars=vars,
            fallback=fallback,
        )
    
    def save(self, file_path):
        with open(file_path, "w") as f:
            self.write(f)

class Backend:
    def __init__(
            self,
            configuration_dir,
            user="",
            ) -> None:
        self.configuration = Configuration(
            directory=configuration_dir,
            user=user)

        self.gpg = gnupg.GPG(
            gnupghome=self.configuration.gett(
                ConfigurationElements.gnupghome.name,
                vars=os.environ),
            gpgbinary=self.configuration.gett(
                ConfigurationElements.gpgbinary.name,
                vars=os.environ)
            )
        self.ensure_api_key_file_existence()
        self.portfolio = Portfolio.byDirectory(
            self.configuration.gett(ConfigurationElements.save_dir.name))

        self.llm:LLM = LLM(
            config_json_path=self.configuration.gett(ConfigurationElements.llm_configs.name))

    def encrypt(self, data):
        return self.gpg.encrypt(
            data,
            self.configuration.gett(
                ConfigurationElements.gpguser.name))
    
    def ensure_api_key_file_existence(self):
        LLM_API_key_file = self.configuration.gett(
            ConfigurationElements.API_Keys.name)
        if not Path(LLM_API_key_file).exists():
            Path(LLM_API_key_file).parent.mkdir(parents=True, exist_ok=True)
            with open(LLM_API_key_file, 'wb') as f:
                f.write(self.encrypt(b'{}').data)

    def api_key_exists(self, api):
        LLM_API_key_file = self.configuration.gett(
            ConfigurationElements.API_Keys.name)
        contains = False
        with open(LLM_API_key_file, 'rb') as f:
            LLM_API_key = self.gpg.decrypt_file(f)
            contains = api in json.loads(LLM_API_key.data)
        return contains

    def read_api_key(self, api):
        LLM_API_key_file = self.configuration.gett(
            ConfigurationElements.API_Keys.name)
        LLM_API_key = None
        with open(LLM_API_key_file, 'rb') as f:
            LLM_API_key = self.gpg.decrypt_file(f)
            LLM_API_key = json.loads(LLM_API_key.data)[api]
        return LLM_API_key

    def write_api_key(self, api, api_key):
        LLM_API_key_file = self.configuration.gett(
            ConfigurationElements.API_Keys.name)
        with open(LLM_API_key_file, 'rb+') as f:
            LLM_API_keys = json.loads(self.gpg.decrypt_file(f).data)
            if not api_key and not api in LLM_API_keys:
                raise ValueError("Missing API Key.")
            if api_key:
                f.seek(0)
                f.truncate()
                LLM_API_keys[api] = api_key
                f.write(
                    self.encrypt(str.encode(json.dumps(LLM_API_keys))).data)

    def get_llm_model_option_names(self):
        return self.llm.get_catalog_options()
    
    def get_llm_api_options(self):
        return list(x.name for x in LLMAPIOptions if not x.value is ...)
    
    def get_default_options(self, api:str):
        api:Model = getattr(LLMAPIOptions, api).value
        return api.default_options()
    
    def get_default_llm_model_name(self):
        return self.llm.get_catalog_default_option()
    
    def set_llm_model(self, model_name, model_options=None, api=None, api_key=None):
        self.llm.set_model(name=model_name, api_option=api)
        if model_options:
            self.llm.set_model_options(options=model_options)

        if not api_key:
            api = self.llm.get_model_API().name
            api_key = self.read_api_key(api=api)

        if api_key is None:
            raise ValueError("Missing API Key.")
        else:
            self.llm.set_api(api_key=api_key)

    def add_llm_model(self, api, api_key, model_name, model_options):
        self.write_api_key(api=api, api_key=api_key)
        self.set_llm_model(
            model_name=model_name,
            model_options=model_options,
            api=getattr(LLMAPIOptions, api),
            api_key=api_key)

    def save_portfolio(self):
        save_dir = Path(self.configuration.gett(
            ConfigurationElements.save_dir.name))
        if not save_dir.exists():
            save_dir.mkdir(parents=True)

        config_file = save_dir / self.configuration.FILENAME
        self.configuration.save(config_file)
        
        port_file =  save_dir / self.portfolio.FILENAME
        self.portfolio.save(port_file)

        self.llm.save_catalog()

    def quicksave_portfolio(self):
        save_dir = Path(self.configuration.gett(
            ConfigurationElements.save_dir.name))
        if not save_dir.exists():
            save_dir.mkdir(parents=True)

        config_file = save_dir / self.configuration.FILENAME
        self.configuration.save(config_file)
        
        port_file =  save_dir / ("~"+self.portfolio.FILENAME)
        self.portfolio.save(port_file)

        self.llm.save_catalog()

    def get_profile_names(self):
        return self.portfolio.getProfileNames()
    
    def select_profile_by_name(self, name):
        return self.portfolio.selectProfileByName(name)
    
    def get_profiles(self):
        return self.portfolio.getProfiles()
    
    def rename_profile(self, profile, name):
        self.portfolio.renameProfile(profile, name)

    def add_profile(self, profile):
        self.portfolio.addProfile(profile)
    
    def historical_posts_iter(self):
        return self.portfolio.getHistoricalPosts().items()
    
    def get_historical_posts(self):
        return self.portfolio.getHistoricalPosts()
    
    def get_last_applied_for_profile_by_name(self, name):
        return self.portfolio.selectProfileByName(name).getLastApplied()