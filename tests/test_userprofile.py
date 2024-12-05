"""
"""
import pytest
import datetime
import dataclasses
from jobsearch.backend.userprofile import(
    UserProfile,
    BasicInfo,
    WorkExperience,
    Projects,
    Education,
    Skills,
    Job,
    Project,
    Credential
)

class TestUserProfile:
    user_profile = UserProfile(
        summary = "test",
        basic_info = BasicInfo(
            name = "A Z",
            email = "a@z.com",
            phone =  "123-456-7890",
            location = "Everywhere, USA",
            linkedInLink = "https://www.linkedin.com/",
            gitHubLink = "https://github.com/",
            website = "https://example.com/",
        ),
        work_experience = WorkExperience(
            jobs = [Job(
                organization = "XYZ LLC",
                position = "Job Doer",
                location = "Nowhere, CA",
                start_date = datetime.date(1900,1,1),
                end_date = datetime.date.today(),
                contributions = ["Action verbed.","Quatified impact.","Succinctly communicated complex, nuanced ideas, comprehensively covering years of experience, without verbiage, by all subjective measures, in 10 characters or fewer."],
            )]
        ),
        projects = Projects(
            projects=[Project(
                organization = "Personal",
                name = "Mars Colony Alpha",
                start_date = datetime.date(2024,1,1),
                end_date = datetime.date(2024,1,2),
                contributions = ["Embodied 'There is no I in team'.","Single handedly ensured the success of the project from the micro to the macro level."],
            )]
        ),
        education = Education(
            credentials=[Credential(
                institution = "Definitely Real University",
                location = "Canada",
                start_date = datetime.date(2015,9,1),
                end_date = datetime.date(2023,8,20),
                contributions = ["Completed degree.","Achieved honors (most improved)."],
            )]
        ),
        skills = Skills(
            skills={
                "Languages":["Pig latin (Fluent)", "English (kinda)"],
                "Technology":["SNES"]
            }
        ),
    )

    def test_resume_recovery_from_dict(self):
        dct_copy = dataclasses.asdict(self.user_profile)
        reinst = UserProfile.from_dict(dct=dct_copy)
        assert reinst == self.user_profile