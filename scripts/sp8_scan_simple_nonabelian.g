# GAP worker for scripts/find_simple_nonabelian_subgroups.py.

if not IsBound(SCRIPT_DIR) then Error("SCRIPT_DIR must be bound"); fi;
if not IsBound(RUN_DIR) then Error("RUN_DIR must be bound"); fi;
if not IsBound(SP8_SIMPLE_SCAN_CONFIG) then Error("SP8_SIMPLE_SCAN_CONFIG must be bound"); fi;
if not IsBound(SP8_SIMPLE_SCAN_OUT_TSV) then Error("SP8_SIMPLE_SCAN_OUT_TSV must be bound"); fi;

Read(Concatenation(SCRIPT_DIR, "/sp8_common.g"));;
Read(SP8_SIMPLE_SCAN_CONFIG);;
Read(Concatenation(RUN_DIR, "/group_model.g"));;

SP8_SimpleScanBool := function(value)
    if value then
        return "true";
    fi;
    return "false";
end;

P := SP8_LoadRep(fail);;
PrintTo(
    SP8_SIMPLE_SCAN_OUT_TSV,
    "rep_id\torder\tcomposition_factor_count\tis_abelian\tis_nonabelian_simple\tstructure\n"
);

processed := 0;;
simple_count := 0;;
for item in SP8_SIMPLE_SCAN_CANDIDATES do
    rep_id := item[1];;
    expected_order := item[2];;
    H := SP8_ReadRep(Concatenation(RUN_DIR, "/reps/rep_", String(rep_id), ".g"), P);;
    order := Size(H);;
    if order <> expected_order then
        Error(Concatenation("order mismatch for rep ", String(rep_id)));
    fi;
    series := CompositionSeries(H);;
    factor_count := Length(series) - 1;;
    is_abelian := IsAbelian(H);;
    is_nonabelian_simple := factor_count = 1 and not is_abelian;;
    structure := "";;
    if is_nonabelian_simple then
        structure := StructureDescription(H);;
        simple_count := simple_count + 1;;
    fi;
    AppendTo(
        SP8_SIMPLE_SCAN_OUT_TSV,
        String(rep_id), "\t",
        String(order), "\t",
        String(factor_count), "\t",
        SP8_SimpleScanBool(is_abelian), "\t",
        SP8_SimpleScanBool(is_nonabelian_simple), "\t",
        structure, "\n"
    );
    processed := processed + 1;;
    if RemInt(processed, 100) = 0 then
        Print("processed ", processed, " / ", Length(SP8_SIMPLE_SCAN_CANDIDATES),
              "; simple ", simple_count, "\n");
    fi;
od;

Print("done ", processed, " candidates; ", simple_count, " nonabelian simple\n");
QUIT_GAP(0);
