import pickle

data = None
with open('./test_data.pkl', 'rb') as f:
    data = pickle.load(f)

print(f"len(data): {len(data)}")

keys = ['id', 'episode_done', 'current_player', 'actor', 'action', 'agent_observation', 'graph_history', 
'graph_state', 'game_text', 'all_text', 'prompt', 'graph_history_dropoutless', 'graph_state_dropoutless', 
'game_text_dropoutless', 'all_text_dropoutless', 'prompt_dropoutless', 'text', 'eval_labels']

print(data[0])

example = data[0]

left_context = example["game_text_dropoutless"]

current_actor = example['current_player']

for key, value in example.items():
    print("-"*100)
    print(key, repr(value))


