#!/usr/bin/env python3
"""Upload Files and Images"""
from models import cloud


def process_files_in_place(attrs: list = [], data: dict = {}, obj=None) -> None:
    for attr in attrs:
        if attr in data:
            image = data.get(attr)
            try:
                public_id = None
                if obj is not None:
                    if hasattr(obj, 'name'):
                        public_id = getattr(obj, 'name', None)
                        if public_id is not None:
                            public_id = str(public_id).replace(
                                ' ', '_') + '_' + attr
                public_id = public_id or attr
                resp = cloud.upload_file(data=image, public_id=public_id)
                data.update({attr: resp.get('url')})
            except Exception as exc:
                raise ValueError(str(exc))
