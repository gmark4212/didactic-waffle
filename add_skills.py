#!/usr/bin/python
from modules.storage import DataStorage


if __name__ == '__main__':
    db = DataStorage()
    with open('skills.txt') as f:
        content = f.readlines()
        content = [x.strip() for x in content]

    db.add_skill_to_ref(content)
    print(content)
