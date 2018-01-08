# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-14 09:29
from __future__ import unicode_literals

import os

from django.conf import settings
from django.db import migrations

import requests

from gepetto_packages.utils import SOURCES, api_headers, api_data

REDMINES = [
    ('https://redmine.laas.fr', os.getenv('REDMINE_TOKEN', '')),
    # ('https://git.openrobots.org', os.getenv('OPENROB_TOKEN', ''),
]
PACKAGES = [
    'openhrp3-hrp2',
    'Pyrene Talos',
]

def redmine(apps, schema_editor):
    Project, License, Package, Repo = (apps.get_model('gepetto_packages', model)
                                       for model in ['Project', 'License', 'Package', 'Repo'])
    dummy_project, _ = Project.objects.get_or_create(name='dummy')
    for api, token in REDMINES:
        headers = api_headers(source=SOURCES.redmine, token=token)
        for data in requests.get(f'{api}/projects.json?limit=100', headers=headers).json()['projects']:
            if data['name'] in PACKAGES:
                Package.objects.get_or_create(name=data['identifier'], project=dummy_project)
            package_qs = Package.objects.filter(name=data['identifier'])
            if package_qs.exists():
                r = Repo.objects.create(package=package_qs.first(), repo_id=data['id'], open_pr=0,
                                        source_type=SOURCES.redmine, api_url=api, token=token)
                repo_data = api_data(r)['project']
                r.homepage = repo_data['homepage']
                r.url = f'{api}/projects/{r.package.name}'
                issues_data = requests.get(f'{api}/issues.json?project_id={r.repo_id}&status_id=open', headers=headers)
                r.open_issues = issues_data.json()['total_count']
                r.save()
                if r.homepage and not r.package.homepage:
                    r.package.homepage = r.homepage
                    r.package.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gepetto_packages', '0003_gitlab'),
    ]

    operations = [
        migrations.RunPython(redmine),
    ]