"""SQLAlchemy models for GitStatsDev"""
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

DB = SQLAlchemy()


class Repo(DB.Model):
    """GitHub Repositories"""
    owner = DB.Column(DB.String(40), primary_key=True)
    name = DB.Column(DB.String(100), primary_key=True)
    description = DB.Column(DB.String(255))
    primary_language = DB.Column(DB.String(100))
    created_at = DB.Column(DB.DateTime)
    updated_at = DB.Column(DB.DateTime)
    disk_usage = DB.Column(DB.BigInteger)
    stars = DB.Column(DB.BigInteger)
    forks = DB.Column(DB.BigInteger)
    total_issues = DB.Column(DB.BigInteger)
    open_issues = DB.Column(DB.BigInteger)
    closed_issues = DB.Column(DB.BigInteger)
    total_PRs = DB.Column(DB.BigInteger)
    open_PRs = DB.Column(DB.BigInteger)
    merged_PRs = DB.Column(DB.BigInteger)
    closed_PRs = DB.Column(DB.BigInteger)
    vulnerabilities = DB.Column(DB.BigInteger)
    unique_PR_authors = DB.Column(DB.BigInteger)
    PR_acceptance_rate = DB.Column(DB.Float)
    median_open_PR_hrs_age = DB.Column(DB.Float)
    median_PR_hrs_to_merge = DB.Column(DB.Float)
    median_PR_hrs_to_close = DB.Column(DB.Float)

    def as_dict(self):
        return {c.name: (getattr(self, c.name)
                         if pd.notna(getattr(self, c.name))
                         else 'N/A')
                for c in self.__table__.columns}
