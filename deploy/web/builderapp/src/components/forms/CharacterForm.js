
/*****
 * Copyright (c) Meta Platforms, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import {
  Button,
  FormGroup,
  Intent,
  InputGroup,
  Switch,
  TextArea,
  Alignment,
} from "@blueprintjs/core";
import { Formik } from "formik";

import BaseSuggest from "./BaseSuggest";

function CharacterForm({ initialInputs, handleSubmit, type }) {
  return (
    <Formik
      initialValues={initialInputs}
      validate={(values) => {
        let errors = {};
        if (!values.name) {
          errors.name = "Required";
        }
        if (!values.name_prefix) {
          errors.name_prefix = "Required";
        }
        if (!values.persona) {
          errors.persona = "Required";
        }
        if (!values.physical_description) {
          errors.physical_description = "Required";
        }
        if (!values.char_type) {
          errors.char_type = "Required";
        }
        if (!values.base_id) {
          errors.base_id = "Required";
        }
        return errors;
      }}
      onSubmit={handleSubmit}
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
          handleChange,
          handleBlur,
          handleSubmit,
          handleReset,
        } = props;

        const handleSwitch = (e) => {
          const { name } = e.target;
          setFieldValue(name, values[name] ? 0 : 1);
        };

        return (
          <form data-testid="form">
            <FormGroup
              label="Name"
              labelInfo="(required)"
              labelFor="name-input"
            >
              <InputGroup
                id="name-input"
                name="name"
                intent={errors.name && touched.name ? Intent.DANGER : null}
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.name}
              />
              {errors.name && touched.name && (
                <div className="form-error">{errors.name}</div>
              )}
            </FormGroup>
            <FormGroup
              label="Name Prefix"
              labelInfo="(required)"
              labelFor="name-prefix-input"
            >
              <InputGroup
                id="name-prefix-input"
                name="name_prefix"
                intent={
                  errors.name_prefix && touched.name_prefix
                    ? Intent.DANGER
                    : null
                }
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.name_prefix}
              />
              {errors.name_prefix && touched.name_prefix && (
                <div className="form-error">{errors.name_prefix}</div>
              )}
            </FormGroup>
            <FormGroup
              label="Persona"
              labelInfo="(required)"
              labelFor="persona-input"
            >
              <TextArea
                id="persona-input"
                name="persona"
                growVertically={true}
                fill={true}
                intent={
                  errors.persona && touched.persona ? Intent.DANGER : null
                }
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.persona}
              />
              {errors.persona && touched.persona && (
                <div className="form-error">{errors.persona}</div>
              )}
            </FormGroup>
            <FormGroup
              label="Physical Description"
              labelInfo="(required)"
              labelFor="physical-description-input"
            >
              <TextArea
                id="physical-description-input"
                name="physical_description"
                growVertically={true}
                fill={true}
                intent={
                  errors.physical_description && touched.physical_description
                    ? Intent.DANGER
                    : null
                }
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.physical_description}
              />
              {errors.physical_description && touched.physical_description && (
                <div className="form-error">{errors.physical_description}</div>
              )}
            </FormGroup>
            <FormGroup
              label="Character Type"
              labelInfo="(required)"
              labelFor="char-type-input"
            >
              <InputGroup
                id="char-type-input"
                name="char_type"
                intent={
                  errors.char_type && touched.char_type ? Intent.DANGER : null
                }
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.char_type}
              />
              {errors.char_type && touched.char_type && (
                <div className="form-error">{errors.char_type}</div>
              )}
            </FormGroup>
            <FormGroup
              label="Base Character"
              labelInfo="(required)"
              labelFor="base-id-input"
            >
              <BaseSuggest
                id="base-id-input"
                name="base_id"
                type={`base_${type}`}
                errors={errors.base_id}
                touched={touched.base_id}
                setFieldTouched={setFieldTouched}
                formValue={values.base_id}
                handleChange={setFieldValue}
              />
              {errors.base_id && touched.base_id && (
                <div className="form-error">{errors.base_id}</div>
              )}
            </FormGroup>
            <FormGroup label="Properties" labelInfo="(required)" large={true}>
              <div style={{ marginLeft: "15px", width: "150px" }}>
                <Switch
                  label="Plural"
                  name="is_plural"
                  onChange={handleSwitch}
                  checked={!!values.is_plural}
                  alignIndicator={Alignment.RIGHT}
                />
              </div>
            </FormGroup>

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
              type="submit"
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

export const emptyCharacterForm = {
  name: "",
  name_prefix: "",
  persona: "",
  physical_description: "",
  char_type: "",
  base_id: 0,
  is_plural: 0,
};

export default CharacterForm;
