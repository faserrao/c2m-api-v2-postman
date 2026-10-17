. as $c
| {
    info: {
      name: env.JQ_INFO_NAME,
      schema: env.JQ_INFO_SCHEMA
    },
    item: $c.item
  }

