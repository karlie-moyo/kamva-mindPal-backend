#!/usr/bin/env python3
"""Cloudinary Module"""
from cloudinary import config, uploader
from fileUploader import FileUpload
import datauri
import os
from typing import Dict
from uuid import uuid4
from PIL import Image

temp_file = 'tmp'


class Cloudinary(FileUpload):
    """Cloudinary Class"""

    def __init__(self, cloud_name, api_key, api_secret):
        """Configure Cloudinary with credentials"""
        config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )

    def upload_file(
        self, file_path=None, data=None,
        public_id=None, resource_type='auto'
    ) -> Dict[str, str]:
        """Uploads file to Cloudinary"""
        if data is not None:
            try:
                data = datauri.parse(data)
                with open(temp_file, 'wb') as f:
                    f.write(data.data)
                file_path = temp_file
            except Exception as e:
                raise ValueError('Error Processing data: ' + str(e))

        # optimize image
        image = Image.open(file_path)
        image.convert('RGB').save(file_path, format='JPEG', optimized=True)

        if public_id is not None:
            public_id = public_id + '_' + str(uuid4())
        try:
            upload_result = uploader.upload(
                file_path, secure=True, public_id=public_id,
                resource_type=resource_type
            )
            os.remove(temp_file)
        except FileNotFoundError:
            pass
        except Exception as e:
            raise ValueError('Error Processing data: ' + str(e))
        return {
            'url': upload_result.get('secure_url'),
            'public_id': upload_result.get('public_id')
        }

    def delete_file(self, public_id):
        try:
            uploader.destroy(public_id)
        except Exception as e:
            raise ValueError('Error deleting file')
