from jobsearch.search.profile import Portfolio
from jobsearch.resumes.llm import LLM

import gnupg
import configparser
import platform
import enum
import os
import json
from pathlib import Path

class ConfigurationElements(enum.Enum):
    save_dir = enum.auto()
    platform = enum.auto()
    API_Keys = enum.auto()
    gnupghome = enum.auto()
    gpgbinary = enum.auto()
    default_llm = enum.auto()

class Configuration(configparser.ConfigParser):
    CONFIG_FILE="config.ini"
    def __init__(
            self,
            directory="./jobs",
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
        self.config_file = directory/Configuration.CONFIG_FILE
        if self.config_file.exists():
            self.read(self.config_file)
        else:
            self.default_config()
        self.platform = platform.system()
    
    def default_config(self):
        self["DEFAULT"] = {
        ConfigurationElements.save_dir.name: str(self.config_file.resolve()),
        ConfigurationElements.platform.name:platform.system(),
        ConfigurationElements.API_Keys.name: "${save_dir}/api_keys.txt.gpg",
        ConfigurationElements.default_llm.name: "google_gemini"
        }
        self['Linux'] = {
            ConfigurationElements.gnupghome.name: "${HOME}/.gnupg",
            ConfigurationElements.gpgbinary.name: "usr/bin/gpg",
        }
        self['Windows'] = {
            ConfigurationElements.gnupghome.name: "${APPDATA}\\gnupg",
            ConfigurationElements.gpgbinary.name: "C:\\Program Files (x86)\\gnupg\\bin\\gpg.exe",
        }

    def get(
            self,
            option,
            *,
            raw=False,
            vars=None,
            fallback=configparser._UNSET):
        super().get(
            section=self.platform,
            option=option,
            raw=raw,
            vars=vars,
            fallback=fallback,
        )

class Backend:
    def __init__(
            self,
            configuration_dir,
            ) -> None:
        self.configuration = Configuration(directory=configuration_dir)

        self.gpg = gnupg.GPG(
            gnupghome=self.configuration.get(
                ConfigurationElements.gnupghome.name,
                vars=os.environ),
            gpgbinary=self.configuration.get(
                ConfigurationElements.gpgbinary.name,
                vars=os.environ)
            )
        self.portfolio = Portfolio.byDirectory(
            self.configuration.get(ConfigurationElements.save_dir.name))

        self.llm:LLM = None
        self.set_llm(
            self.configuration.get(ConfigurationElements.default_llm.name))

    def set_llm(self, option):
        LLM_API_key_file = self.configuration.get(
            ConfigurationElements.API_Keys.name)
        with open(LLM_API_key_file, 'rb') as f:
            LLM_API_key = self.gpg.decrypt_file(f)
            LLM_API_key = getattr(
                json.loads(LLM_API_key.data),
                option
                )
        self.llm = LLM(api_key=LLM_API_key)
