class ObjectRandomizer {
    constructor(selected_list_size = 10) {
        this.object_list = require('./object_mock_db.json')["object_list"];
        this.selected_list_size = 10;
        this.primary_object_name = "";
    }

    get_primary_object() {
        this.primary_object_name = this.object_list[Math.floor(Math.random() * this.object_list.length)];
        return this.primary_object_name;
    }

    get_object_list() {
        let selected_list = []

        while (selected_list.length < this.selected_list_size) {
            let random_object = this.object_list[Math.floor(Math.random() * this.object_list.length)];
            if (random_object != this.primary_object_name) {
                selected_list.push(random_object);
            }
        }

        return selected_list;
    }
}

export { ObjectRandomizer }
