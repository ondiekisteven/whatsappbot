import boto3


class S3Uploader:
    def __init__(self):
        self.KEY = 'AKIAZSJC5QSQVBBKCQOF'
        self.TOKEN = 'jwg18EBwh6InT5fteeA0Uk9xJdhiKHhEP0KX4j0g'
        self.service = 's3'
        self.bucket = 'som-whatsapp'

    @property
    def client(self):

        s3 = boto3.client(
            self.service,
            aws_access_key_id=self.KEY,
            aws_secret_access_key=self.TOKEN
        )
        return s3

    def upload_file(self, file_name, object_name):
        self.client.upload_file(file_name, self.bucket, object_name)

    def delete_file(self, file_name):
        self.client.delete_object(Bucket=self.bucket, Key=f'music/{file_name}')
