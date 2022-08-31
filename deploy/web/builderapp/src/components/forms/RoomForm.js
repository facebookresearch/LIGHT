/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import {
  Button,
  FormGroup,
  Intent,
  InputGroup,
  TextArea,
} from "@blueprintjs/core";
import { Formik } from "formik";

import BaseSuggest from "./BaseSuggest";

function RoomForm({ initialInputs, handleSubmit, type }) {
  return (
    <Formik
      initialValues={initialInputs}
      validate={(values) => {
        let errors = {};
        if (!values.name) {
          errors.name = "Required";
        }
        if (!values.description) {
          errors.description = "Required";
        }
        if (!values.backstory) {
          errors.backstory = "Required";
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
              label="Description"
              labelInfo="(required)"
              labelFor="description-input"
            >
              <TextArea
                id="description-input"
                name="description"
                growVertically={true}
                fill={true}
                intent={
                  errors.description && touched.description
                    ? Intent.DANGER
                    : null
                }
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.description}
              />
              {errors.description && touched.description && (
                <div className="form-error">{errors.description}</div>
              )}
            </FormGroup>
            <FormGroup
              label="Backstory"
              labelInfo="(required)"
              labelFor="backstory-input"
            >
              <TextArea
                id="backstory-input"
                name="backstory"
                growVertically={true}
                fill={true}
                intent={
                  errors.backstory && touched.backstory ? Intent.DANGER : null
                }
                onBlur={handleBlur}
                onChange={handleChange}
                value={values.backstory}
              />
              {errors.backstory && touched.backstory && (
                <div className="form-error">{errors.backstory}</div>
              )}
            </FormGroup>
            <FormGroup
              label="Base Room"
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

export const emptyRoomForm = {
  name: "",
  description: "",
  backstory: "",
  base_id: 0,
};

export default RoomForm;
