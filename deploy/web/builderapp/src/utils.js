/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";

import CONFIG from "./config";

const BASE_URL =
  CONFIG.port != "80" ? `${CONFIG.host}:${CONFIG.port}` : CONFIG.host;

export function usePrevious(value) {
  const ref = React.useRef();
  React.useEffect(() => {
    ref.current = value;
  });
  return ref.current;
}

export function useDidChange(val) {
  const prevVal = usePrevious(val);
  return prevVal !== val;
}

export function useAPI(CONFIG, url, { body, params } = {}, preloaded) {
  const [state, setState] = React.useState({
    loading: true,
    result: undefined,
  });

  const newUrl = useDidChange(url);

  React.useEffect(() => {
    if (state.loading && preloaded) {
      setState({ loading: false, result: preloaded });
      return;
    }
    if (newUrl) {
      setState({ loading: true, result: undefined });
      return;
    }
    let isSubscribed = true;

    if (state.loading) {
      var target_url = BASE_URL + "/builder" + url;
      fetch(target_url, { credentials: "same-origin" })
        .then((res) => res.json())
        .then((data) => {
          if (isSubscribed) {
            setState({ loading: false, result: data });
          }
        })
        .catch((err) =>
          console.log("Error fetching data for url: " + target_url, err)
        );
    }

    return () => (isSubscribed = false);
  }, [CONFIG.host, CONFIG.port, url, newUrl, preloaded, state]);

  const reload = () => {
    setState({ loading: true, result: undefined });
  };

  return {
    loading: state.loading,
    result: state.result,
    reload,
  };
}

export function post(url, payload) {
  const formBody = [];
  for (let property in payload) {
    const encodedKey = encodeURIComponent(property);
    const encodedValue = encodeURIComponent(
      typeof payload[property] === "object"
        ? JSON.stringify(payload[property])
        : payload[property]
    );
    formBody.push(encodedKey + "=" + encodedValue);
  }
  return fetch(`${BASE_URL}/${url}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    credentials: "same-origin",
    body: formBody.join("&"),
  });
}

export function get_source(local_id, entities) {
  if (local_id in entities.room) {
    return entities.room[local_id].id;
  } else if (local_id in entities.object) {
    return entities.object[local_id].id;
  } else if (local_id in entities.character) {
    return entities.character[local_id].id;
  } else {
    return 0;
  }
}
