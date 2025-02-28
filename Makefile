run:
	docker run -it -d --env-file .env --restart=unless-stopped --name easy_refer fin_bot
stop:
	docker stop easy_refer
attach:
	docker attach easy_refer
dell:
	docker rm easy_refer