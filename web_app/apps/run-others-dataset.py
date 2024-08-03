import os
import sqlite3


from apps.predict_on_video import predict_on_video, SEQUENCE_LENGTH

# Define the path to the 'other-datasets' folder
base_path = 'C:/Users/Phi/Desktop/suspicious-detection-phimhn/other-datasets'

# List of dataset folders
datasets = ['walking']

db_path = 'run_with_other_dataset.db'  # Path to your SQLite database file

# Connect to SQLite database
conn = sqlite3.connect(db_path)

# Open connection
cursor = conn.cursor()

# Create table with unique constraint
cursor.execute('''
    CREATE TABLE IF NOT EXISTS action_folders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset TEXT NOT NULL,
        action TEXT NOT NULL,
        video_name TEXT NOT NULL,
        recoginize_actions TEXT NOT NULL,
        is_contains TEXT,
        UNIQUE(dataset, action, video_name)
    )
''')
# Commit changes and close connection
conn.commit()



def process(filepath, dataset, action, video_name):
    if filepath.lower().endswith(".mp4") or filepath.lower().endswith(".avi"):
        print('-- Start process video file: ' + filepath)
        save_path = os.path.join('test', filepath)
        try:
            output_path, result, detects, total_seconds = predict_on_video(save_path, SEQUENCE_LENGTH)
            recoginize_actions = ', '.join(result)
            is_contains = 'not contains'
            if (action == 'walking'):
                is_contains = 'contains'
            elif recoginize_actions.index(action) >= 0:
                is_contains = 'contains'
            cursor = conn.cursor()
            # Upsert into SQLite database
            cursor.execute('''INSERT OR REPLACE INTO action_folders (dataset, action, video_name, recoginize_actions, is_contains)
                                                        VALUES (?, ?, ?, ?, ?)
                                                        ''',
                           (dataset, action, video_name, recoginize_actions, is_contains))
            # Commit changes and close connection
            conn.commit()
            # conn.close()
        except Exception as e:
            print(e)
            print('Error video, mannual check: ', filepath)

# Iterate over each dataset folder
for dataset in datasets:
    dataset_path = os.path.join(base_path, dataset)
    if os.path.isdir(dataset_path):
        print(f"Dataset: {dataset}")

        # Iterate over each action folder in the dataset
        for folder_name in os.listdir(dataset_path):
            action_folder_path = os.path.join(dataset_path, folder_name)
            if os.path.isdir(action_folder_path):
                print(f"  Action folder: {folder_name}")
                for file_name in os.listdir(action_folder_path):
                    file_path = os.path.join(action_folder_path, file_name)
                    # Check if file is a video file
                    if os.path.isdir(file_path):
                        for sub_file_name in os.listdir(file_path):
                            sub_file_path = os.path.join(file_path, sub_file_name)
                            process(sub_file_path, dataset, folder_name, sub_file_name)
                    else:
                        process(file_path, dataset, folder_name, file_name)


    else:
        print(f"Dataset folder {dataset} does not exist.")
conn.close()