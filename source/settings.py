S3_CONFIGURATIONS = {
    "service_name": "s3",
    "aws_access_key_id": "GLZG2JTWDFFSCQVE7TSQ",
    "aws_secret_access_key": "VjTXOpbhGvYjDJDAt2PNgbxPKjYA4p4B7Btmm4Tw",
    "endpoint_url": "http://10.12.1.149:8000/",
    "bucket": "ai-pipeline-raw-data",
    "base_path_s3": 's3://ai-pipeline-raw-data/'
}

BOTO3_CONFIGURATIONS = {
    "max_attempts": 50,
    "mode": "standard"
}

BOOTSTRAP_SERVERS = {
    "research_ai" : [
            "kafka01.research.ai",
            "kafka02.research.ai",
            "kafka03.research.ai",
        ],
    
    "production_bt": [
        "kafka01.production02.bt",
        "kafka02.production02.bt",
        "kafka03.production02.bt",
        "kafka04.production02.bt",
        "kafka05.production02.bt",
        "kafka06.production02.bt",
    ]
}

BEANSTALK = {
    "host": "192.168.150.21",
    "port": "11300"
}

CDP = {
    'connection': 'http://10.12.3.30:9125/'
}


# "git update-index --skip-worktree settings.py"
# "git update-index --no-skip-worktree settings.py"

