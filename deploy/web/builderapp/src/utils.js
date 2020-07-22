import React from "react";

import CONFIG from "./config";

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
      fetch(CONFIG.host + ":" + CONFIG.port + "/builder" + url)
        .then((res) => res.json())
        .then((data) => {
          if (isSubscribed) {
            setState({ loading: false, result: data });
          }
        })
        .catch((err) => console.log("Error fetching data"));
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
  return fetch(`${CONFIG.host}:${CONFIG.port}/${url}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formBody.join("&"),
  });
}
