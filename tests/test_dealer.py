from os import path as op, environ
import pytest
from sys import version_info
from datetime import datetime


def test_git():

    from dealer.git import git, Backend

    assert git.repo
    assert git.revision
    assert git.tag
    assert git.revision_date
    assert type(git.revision_date) is datetime

    git.path = 'invalid/path/to/git'
    assert not git._repo

    with pytest.raises(TypeError):
        assert git.repo

    git.path = op.abspath(op.dirname(op.dirname(__file__)))
    assert git.repo

    git = Backend('.')
    assert git.repo


@pytest.mark.skipif(version_info > (3, 0), reason='requires python2')
def test_hg():
    from dealer.mercurial import hg, Backend

    path = op.join(op.dirname(__file__), 'hg')
    hg.path = path
    assert hg.repo
    assert hg.revision
    assert hg.tag
    assert hg.revision_date
    assert type(hg.revision_date) is datetime

    hg.path = 'invalid/path/to/hg'
    assert not hg._repo

    hg = Backend(path)
    assert hg.repo


def test_simple():
    from dealer.simple import simple, Backend

    path = op.join(op.dirname(__file__), 'simple')
    simple.path = path
    assert simple.repo
    assert simple.revision == 'default'
    assert simple.tag == 'default'
    assert simple.revision_date
    assert type(simple.revision_date) is datetime

    simple.path = 'invalid/path/to/hg'
    assert not simple._repo

    with pytest.raises(TypeError):
        assert simple.repo

    simple = Backend(op.join(path, 'revision'))
    assert simple.revision == 'test_revision'

    simple = Backend(path, filename='revision2')
    assert simple.revision == 'cap1254'


def test_env():
    from dealer.env import env, Backend
    from dateutil.parser import parse

    environ['DEALER_REVISION'] = '3ffb6b6'
    environ['DEALER_TAG'] = 'v1.0'
    environ['DEALER_REVISION_DATE'] = '2010-05-08T23:41:54.000Z'

    assert env.revision == '3ffb6b6'
    assert env.tag == 'v1.0'
    assert type(env.revision_date) is datetime
    assert env.revision_date == parse('2010-05-08T23:41:54.000Z')

    environ['MY_REVISION'] = '3ffb6b7'
    environ['MY_TAG'] = 'v1.1'
    environ['MY_REVISION_DATE'] = '2010-06-08T23:41:54.000Z'

    options = dict(revision_env_keyname='MY_REVISION',
                   tag_env_keyname='MY_TAG',
                   revision_date_env_keyname='MY_REVISION_DATE')
    env = Backend(**options)
    assert env.revision == '3ffb6b7'
    assert env.tag == 'v1.1'
    assert type(env.revision_date) is datetime
    assert env.revision_date == parse('2010-06-08T23:41:54.000Z')


def test_auto():
    from dealer.auto import auto
    from dealer.git import git

    path = op.join(op.dirname(__file__), 'hg')
    auto.path = path
    assert auto.repo
    assert auto.revision
    assert auto.revision_date

    auto.path = git.path
    assert auto.repo
    assert auto.revision == git.revision


def test_common():
    from dealer import get_backend

    git = get_backend('git')
    assert git.repo


def test_backends():
    from dealer import get_backend

    path = op.dirname(__file__)
    auto = get_backend('auto', path=path, backends=('simple', 'git'))
    assert auto.repo


def test_null():
    from dealer.null import null

    assert null.repo


def test_flask():
    from flask import Flask, g
    from dealer.contrib.flask import Dealer

    app = Flask('test')
    Dealer(app)
    assert app.revision

    app.route('/')(lambda: "%s - %s - %s" % (g.revision,
                                             g.tag,
                                             g.revision_date.strftime('%c')))
    with app.test_request_context():
        client = app.test_client()
        response = client.get('/')
        assert app.revision in response.data.decode('utf-8')
        assert app.tag in response.data.decode('utf-8')
        assert type(app.revision_date) is datetime
        assert (app.revision_date.strftime('%c')
                in response.data.decode('utf-8'))


def test_django():
    import os
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.django_app.settings'

    from django.test import Client

    client = Client()
    revision = client.get('/revision/')
    assert revision.status_code == 200
    assert revision.content

    tag = client.get('/tag/')
    assert tag.status_code == 200
    assert tag.content

    revision_date = client.get('/revision_date/')
    assert revision_date.status_code == 200
    assert revision_date.content


def test_pyramid():
    from tests.pyramid_app import revision, config
    from pyramid import testing
    testing.setUp(config.registry)
    r = testing.DummyRequest()
    result = revision(r)
    assert result.status_code == 200
    testing.tearDown()
