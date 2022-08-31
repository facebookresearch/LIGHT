
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { Formik } from "formik";
import {
  FormGroup,
  Button,
  Intent,
  Classes,
  Divider,
  Icon,
} from "@blueprintjs/core";
import { isEmpty } from "lodash";

import ColorPicker from "./ColorPicker";
import BaseSuggest from "./BaseSuggest";
import BaseMultiSelect from "./BaseMultiSelect";
import { TILE_COLORS, findBiome, findEmoji } from "../worldbuilding/utils";

export const emptyTileForm = {
  room: undefined,
  characters: [],
  objects: [],
  color: TILE_COLORS[0],
};

function TileForm({
  initialInputs,
  onSubmit,
  onClear,
  entities,
  findOrAddEntity,
  setShowAdvanced,
  selected,
  setSelected,
  neighbor,
}) {
  return (
    <Formik
      initialValues={isEmpty(initialInputs) ? emptyTileForm : initialInputs}
      validate={(values) => {
        let errors = {};
        if (isNaN(values.room)) {
          errors.room = "Required";
        }
        return errors;
      }}
      onSubmit={onSubmit}
    >
      {(props) => {
        const {
          values,
          setFieldValue,
          touched,
          setFieldTouched,
          errors,
          dirty,
          isValid,
          handleSubmit,
          handleReset,
        } = props;

        const setRoomValue = (name, value, fullValue) => {
          setFieldValue(name, value);
          setFieldValue("color", findBiome(fullValue.name, values.color));
        };

        const hasContent = () => {
          return (
            !isNaN(values.room) ||
            !isEmpty(values.characters) ||
            !isEmpty(values.objects)
          );
        };

        return (
          <form>
            <div
              style={{
                display: "flex",
                flexDirection: "row",
                alignContent: "stretch",
                justifyContent: "space-between",
              }}
            >
              <h5 style={{ fontSize: "18px" }} className={Classes.HEADING}>
                <Icon color="#5c7080" iconSize={20} icon="edit" /> Tile Editor
              </h5>
              <div
                style={{
                  display: "flex",
                  justifyContent: "flex-end",
                }}
                onClick={() => {
                  setSelected({ ...selected, data: { ...values } });
                  setShowAdvanced(true);
                }}
              >
                <Button icon="build" />
              </div>
            </div>
            <Divider />
            <FormGroup
              label="Room"
              labelInfo="(required)"
              labelFor="room-input"
            >
              <BaseSuggest
                id="room-input"
                name="room"
                type="room"
                errors={errors.room}
                touched={touched.room}
                setFieldTouched={setFieldTouched}
                formValue={values.room}
                handleChange={setRoomValue}
                entities={entities}
                onItemSelect={findOrAddEntity}
                suggestionSource={neighbor}
              />
              {errors.room && touched.room && (
                <div className="form-error">{errors.room}</div>
              )}
            </FormGroup>
            <ColorPicker
              colors={TILE_COLORS}
              value={values.color}
              handleChange={setFieldValue}
            />
            <FormGroup label="Characters in Room" labelFor="characters-input">
              <BaseMultiSelect
                id="characters-input"
                name="characters"
                type="character"
                errors={errors.characters}
                touched={touched.characters}
                setFieldTouched={setFieldTouched}
                formValue={values.characters}
                handleChange={setFieldValue}
                tooltip="persona"
                entities={entities}
                onItemSelect={(e, type) => {
                  e.emoji = findEmoji(e.name);
                  return findOrAddEntity(e, type);
                }}
                suggestionSource={values.room}
              />
              {errors.characters && touched.characters && (
                <div className="form-error">{errors.characters}</div>
              )}
            </FormGroup>
            <FormGroup label="Objects in Room" labelFor="objects-input">
              <BaseMultiSelect
                id="objects-input"
                name="objects"
                type="object"
                errors={errors.objects}
                touched={touched.objects}
                setFieldTouched={setFieldTouched}
                formValue={values.objects}
                handleChange={setFieldValue}
                tooltip="physical_description"
                entities={entities}
                onItemSelect={(e, type) => {
                  e.emoji = findEmoji(e.name);
                  return findOrAddEntity(e, type);
                }}
                suggestionSource={values.room}
              />
              {errors.objects && touched.objects && (
                <div className="form-error">{errors.objects}</div>
              )}
            </FormGroup>

            <Button
              type="reset"
              onClick={onClear}
              disabled={!hasContent()}
              style={{ marginRight: "15px" }}
            >
              Clear
            </Button>
            <Button
              type="reset"
              onClick={handleReset}
              disabled={!dirty}
              style={{ marginRight: "15px" }}
            >
              Reset
            </Button>
            <Button
              intent={Intent.PRIMARY}
              onClick={handleSubmit}
              disabled={!dirty || !isValid}
              style={{ marginLeft: "15px" }}
            >
              Save Changes
            </Button>
          </form>
        );
      }}
    </Formik>
  );
}

export default TileForm;
