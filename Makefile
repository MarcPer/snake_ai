.PHONY: run_ppo2

run_ppo2:
	@./game.py --speed 100 --controller sb:ppo2 ppo2_model1 --grid_size 4

