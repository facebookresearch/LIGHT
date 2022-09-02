import os
import json

model_folder_prefix = "/checkpoint/light/common_sense/model_data/bart_compare_largersweep_Sun_Aug_14"
eval_folder_prefix = "/checkpoint/light/common_sense/model_data/bart_compare_largersweep_Sun_Aug_14/eval_reports"
world_log_folder_prefix = "/checkpoint/light/common_sense/model_data/bart_compare_largersweep_Sun_Aug_14/world_logs"

model_names = [
    '341', 'c8f'
]

# dts = ["train:evalmode", "test", "valid"]

# dts = ["test"]
dts = ["train:evalmode"]

teachers = "internal:light_common_sense:GameActionsNarrationTeacher,internal:light_common_sense:UseEventGameActionsNarrationTeacher,internal:light_common_sense:SelfPlayNarrationTeacher,internal:light_common_sense:InvalidSelfPlayNarrationTeacher"
# teachers = "internal:light_common_sense:UseEventGameActionsNarrationTeacher"
ignore_existing = True

for dt in dts:
    for model_name in model_names:
        # quickly check if this eval report has already been generated so we could skip
        exists = False
        try:
            with open(f"{eval_folder_prefix}/{dt}_{model_name}.json", "r") as f:
                d = f.read()
            exists = True
        except:
            exists = False

        if exists and not ignore_existing:
            continue
        
        # hacky but the easiest way to see if this model is a "grounded" model is if a grounded 
        # teacher is in the stderr file
        files = os.listdir(f"{model_folder_prefix}/{model_name}/")
        fname = [f for f in files if "stderr" in f][0]
        with open(f"{model_folder_prefix}/{model_name}/{fname}", 'r') as f:
            d = f.read()
        grounded = "internal:light_common_sense:AddCharacterWieldingTeacher" in d

        # make a folder for world_logs
        os.system(f"mkdir {world_log_folder_prefix}/{model_name}/")
        
        # force change train (dt is still useful for file names)
        datatype = "train:evalmode" if dt == "train" else dt
        
        eval_task = """parlai eval_model -t $TEACHERS$ \
            --datatype test \
            --skip-generation false \
            --room-name-do 0 \
            --room-description-do 0.0 \
            --room-backstory-do 0.0 \
            --room-objects-do 0.0 \
            --room-characters-do 0.0 \
            --contained-objects-do 0 \
            --worn-objects-do 0 \
            --wielded-objects-do 0 \
            --carrying-objects-do 0 \
            --attribute-do 0.0 \
            --persona-do 0.0 \
            --phys-description-do 0.0 \
            --character-inside-room-do 0.0 \
            --character-type-do 0.0 \
            --object-inside-room-do 0.0 \
            --object-type-do 0.0 \
            --no-mutation-weight 0.0 \
            --no-mutation-control False \
            --dialog-history-do 0.0 \
            --state-mutations-history-do 0.0 \
            --graph-state-do 0.0 \
            --object-info-do 0.0 \
            --character-info-do 0.0 \
            --graph-input-do 1 \
            --game-text-do 0 \
            --random-use-event-insertion 0.0 \
            --special-tok-lst ' -=- ,IS_TYPE,IS_INSIDE,IS_CARRYING,IS_WIELDING,IS_WEARING,HAS_BACKSTORY,HAS_PERSONA,HAS_DESCRIPTION,IS_DEAD,HAS_DAMAGE_LEVEL,HAS_HEALTH_LEVEL,HAS_STRENGTH_LEVEL,HAS_PLAYER_CONTEXT,HAS_ATTRIBUTE,IS_GETTABLE,IS_DRINK,IS_FOOD,IS_CONTAINER,IS_SURFACE,IS_WEARABLE,IS_WIELDABLE,HAD_SAID,HAD_ACTED,OBSERVED,CONTAINS,CURRENT_PLAYER,ADD,DEL,NO_MUTATION,NO_MUTATION_WEIGHT' \
            """
        eval_task += f"--model-file '{model_folder_prefix}/$MODELNAME$/model' "
        eval_task += f"--report-filename '{eval_folder_prefix}/{dt}_$MODELNAME$.json' "
        if dt == "test":
            # only save world logs for test to save space and re-use for evaluations
            eval_task += f" --world-logs '{world_log_folder_prefix}/$MODELNAME$/$MODELNAME$'"

        eval_task = eval_task.replace("$MODELNAME$", model_name)
        eval_task = eval_task.replace("$TEACHERS$", teachers)
        eval_task = eval_task.replace("--datatype test", f"--datatype {datatype}")
        print(eval_task)
        # break
        os.system(eval_task)
        # break

        print("FINISHED, ADDING GROUNDED TO REPORT")


        # so we don't have to do this hacky fix again, save whether this model was grounded
        with open(f"{eval_folder_prefix}/{dt}_{model_name}.json", "r") as f:
            d = f.read()
        report = json.loads(d)
        report["MANUAL_GROUNDED"] = grounded

        with open(f"{eval_folder_prefix}/{dt}_{model_name}.json", "w") as f:
            f.write(json.dumps(report))
        print("-"*100)

    