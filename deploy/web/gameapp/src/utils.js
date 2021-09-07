export function zipToObject(keys, values) {
  return keys.reduce((obj, k, i) => ({ ...obj, [k]: values[i] }), {});
}

export function setCaretPosition(elem, caretPos) {
  /* inspired from: https://stackoverflow.com/a/512542 */
  if (elem != null) {
    if (elem.createTextRange) {
      var range = elem.createTextRange();
      range.move("character", caretPos);
      range.select();
    } else {
      if (elem.selectionStart) {
        elem.focus();
        elem.setSelectionRange(caretPos, caretPos);
      } else elem.focus();
    }
  }
}

export const DefaultEmojiMapper = (name) => {
  let characterName = name;
  characterName = characterName.replace(/-/g, "_");
  characterName = characterName.replace(/ /g, "_");
  characterName = characterName.toLowerCase();
  const EmojiMap = {
    assassin: "dagger_knife",
    assistant_chef: "hocho",
    bandit: "crossed_swords",
    battle_master: "trident",
    big_sheep_like_brown_dog: "dog2",
    bighorn_sheep: "ram",
    butler: "bellhop_bell",
    drunk_reeling_out_of_the_saloon: "beer",
    fox: "fox_face",
    goblin: "smiling_imp",
    graveyard_keeper: "coffin",
    groundskeeper: "seedling",
    half_wild_cat: "tiger",
    jailer: "old_key",
    lady_of_the_house: "princess",
    lord: "crown",
    master_at_arms: "shield",
    milk_man: "glass_of_milk",
    monkey_friend: "monkey",
    pig: "pig",
    priest: "church",
    rat: "rat",
    serving_boy: "boy",
    skeleton_assistant: "skull",
    small_aggressive_looking_dog: "dog",
    smith: "hammer",
    town_doctor: "syringe",
  };

  return EmojiMap[characterName];
};
