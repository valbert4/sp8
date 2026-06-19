# GAP worker for scripts/count_total_subgroups.py.

if not IsBound(SCRIPT_DIR) then Error("SCRIPT_DIR must be bound"); fi;
if not IsBound(RUN_DIR) then Error("RUN_DIR must be bound"); fi;
if not IsBound(SP8_NORMALIZER_COUNT_CONFIG) then Error("SP8_NORMALIZER_COUNT_CONFIG must be bound"); fi;
if not IsBound(SP8_NORMALIZER_COUNT_OUT_TSV) then Error("SP8_NORMALIZER_COUNT_OUT_TSV must be bound"); fi;

Read(Concatenation(SCRIPT_DIR, "/sp8_common.g"));;
Read(SP8_NORMALIZER_COUNT_CONFIG);;
Read(Concatenation(RUN_DIR, "/group_model.g"));;

P := SP8_LoadRep(fail);;
ambient_order := Size(P);;

processed := 0;;
for item in SP8_NORMALIZER_COUNT_REPS do
    rep_id := item[1];;
    expected_order := item[2];;
    H := SP8_ReadRep(Concatenation(RUN_DIR, "/reps/rep_", String(rep_id), ".g"), P);;
    order := Size(H);;
    if order <> expected_order then
        Error(Concatenation("order mismatch for rep ", String(rep_id)));
    fi;
    start_ms := Runtime();;
    normalizer := Normalizer(P, H);;
    elapsed_ms := Runtime() - start_ms;;
    normalizer_order := Size(normalizer);;
    if RemInt(ambient_order, normalizer_order) <> 0 then
        Error(Concatenation("normalizer order does not divide ambient order for rep ", String(rep_id)));
    fi;
    conjugacy_class_size := QuoInt(ambient_order, normalizer_order);;
    AppendTo(
        SP8_NORMALIZER_COUNT_OUT_TSV,
        String(rep_id), "\t",
        String(order), "\t",
        String(normalizer_order), "\t",
        String(conjugacy_class_size), "\t",
        String(elapsed_ms), "\n"
    );
    processed := processed + 1;;
    if RemInt(processed, 10) = 0 then
        Print("processed ", processed, " / ", Length(SP8_NORMALIZER_COUNT_REPS), "\n");
    fi;
od;

Print("done ", processed, " normalizer computations\n");
QUIT_GAP(0);
