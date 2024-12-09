# import atexit
#
# from rabbit_config.rabbit import RabbitMQ
# from output.driver import OutputDriver
#
#
# class RabbitMQOutputDriver(OutputDriver):
#     name = "rabbitmq"
#
#     def __init__(
#         self,
#         username: str = "guest",
#         password: str = "guest",
#         queue: str = "queue-testing",
#         exchange_name: str = "test",
#         exchange_type: str = "topic",
#         routing_key: str = "hehe",
#         host: str = "192.168.114.40",
#         port: int = 5672,
#         *args,
#         **kwargs
#     ):
#         super(RabbitMQOutputDriver, self).__init__(*args, **kwargs)
#
#         self.rabbitConfig = RabbitMQ(
#             host=host,
#             port=port,
#             username=username,
#             password=password,
#             queue=queue,
#             exchange_name=exchange_name,
#             exchange_type=exchange_type,
#             routing_key=routing_key,
#         )
#         atexit.register(self.close)
#
#     def put(self, output: str, **kwargs):
#         self.rabbitConfig.produce_message(output)
#
#     def close(self):
#         self.rabbitConfig.connection.close()
