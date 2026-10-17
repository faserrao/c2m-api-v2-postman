def deepmerge(a; b):
  reduce (b | to_entries[]) as $i (a;
    if .[$i.key] == null then
      .[$i.key] = $i.value
    elif ($i.value | type) == "object" and (.[$i.key] | type == "object") then
      .[$i.key] = deepmerge(.[$i.key]; $i.value)
    elif ($i.value | type) == "array" and (.[$i.key] | type == "array") then
      .[$i.key] = (.[$i.key] + $i.value | unique)
    else
      .[$i.key] = $i.value
    end
  );
deepmerge(.[0]; .[1])
