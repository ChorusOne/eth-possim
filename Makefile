.PHONY: freshrun

ifdef CONFIG
  GEN_CMD :=python3 -m eth_possim generate --config "$(CONFIG)"
else
  GEN_CMD :=python3 -m eth_possim generate
endif

fresh: clean gen up

freshgen: clean gen

freshrun: clean gen run

gen:
	$(GEN_CMD)

clean:
	rm -rf .data/*

up:
	tilt up --legacy

run:
	tilt up --stream

test:
	pip3 install -r requirements-dev.txt
	PYTHONPATH=. pytest tests/ -svx
