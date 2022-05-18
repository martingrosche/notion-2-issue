import json
import os

import pytest

from utils.NotionHelper import NotionHelper

titles = ["Sample Two", "Sample One"]
bodies = ["My Sample Body 2", "My Sample Body 1"]
assignees = [[], ["martingrosche"]]
labels = [["bug"], ["feature request"]]


def notion_helper():
    results = os.path.join(os.path.dirname(__file__), "..", "resources", "results.json")
    with open(results) as json_file:
            data = json.load(json_file)
    helper = []

    for d in data:
        helper.append(NotionHelper(d.get("properties")))
    return helper

def title_params():
    params = zip(notion_helper(), titles)
    return list(params)

def body_params():
    params = zip(notion_helper(), bodies)
    return list(params)

def multi_params():
    params = zip(notion_helper(), assignees, labels)
    return list(params)


@pytest.mark.parametrize('helper, title', title_params())
def test_get_title(helper, title):
    assert helper.get_title("Title") == title
    with pytest.raises(ValueError) as e:
        helper.get_title(2)
    assert str(e.value) == "Input argument has to be of type string." 

@pytest.mark.parametrize('helper, body', body_params())
def test_get_rich_text(helper, body):
    assert helper.get_rich_text("Discription") == body
    with pytest.raises(ValueError) as e:
        helper.get_rich_text(2)
    assert str(e.value) == "Input argument has to be of type string." 

@pytest.mark.parametrize('helper, assigne, label', multi_params())
def test_get_multi_select(helper, assigne, label):
    assert helper.get_multi_select("Assignees") == assigne
    assert helper.get_multi_select("Labels") == label
    with pytest.raises(ValueError) as e:
        helper.get_multi_select(2)
    assert str(e.value) == "Input argument has to be of type string." 
