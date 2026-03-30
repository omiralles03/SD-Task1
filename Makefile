REDIS_CONTAINER = redis_server
RABBIT_CONTAINER = rabbitmq_server
QUEUE_NAME = ticket_queue

.PHONY: flush-redis purge-rabbit clear-all status help

help:
	@echo "Comandes disponibles:"
	@echo "  make flush-redis  - Delete all Redis data"
	@echo "  make purge-rabbit - Empty RabbitMQ queue"
	@echo "  make clear-all    - Clean Redis + RabbitMQ"
	@echo "  make status       - Show queue and key count"

flush-redis:
	@echo "Cleaning Redis..."
	docker exec -it $(REDIS_CONTAINER) redis-cli flushall

purge-rabbit:
	@echo "Purging RabbitMQ queue: $(QUEUE_NAME)..."
	docker exec -it $(RABBIT_CONTAINER) rabbitmqctl purge_queue $(QUEUE_NAME)

clear-all: flush-redis purge-rabbit
	@echo "Everything is clean! ✨"

status:
	@echo "--- RabbitMQ Queues ---"
	docker exec -it $(RABBIT_CONTAINER) rabbitmqctl list_queues
	@echo -e "\n--- Redis Keys Count ---"
	docker exec -it $(REDIS_CONTAINER) redis-cli dbsize
	@echo -e "\n--- Redis Keys Reqs: ---"
	docker exec -it $(REDIS_CONTAINER) redis-cli --scan --pattern "req:*" | wc -l
	@echo -e "\n--- Redis Keys Seats: ---"
	docker exec -it $(REDIS_CONTAINER) redis-cli --scan --pattern "seat:*" | wc -l
