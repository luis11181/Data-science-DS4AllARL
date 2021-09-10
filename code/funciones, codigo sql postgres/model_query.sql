-- View: public.model_query

-- DROP MATERIALIZED VIEW public.model_query;

CREATE MATERIALIZED VIEW public.model_query
TABLESPACE pg_default
AS
 WITH corte_retiro AS (
         SELECT fdempresas_descripcion.numero,
            fdempresas_descripcion.corte,
            fdempresas_descripcion.retiro
           FROM fdempresas_descripcion
          WHERE ((fdempresas_descripcion.numero, fdempresas_descripcion.corte) IN ( SELECT fdempresas_descripcion_1.numero,
                    max(fdempresas_descripcion_1.corte) AS max_corte
                   FROM fdempresas_descripcion fdempresas_descripcion_1
                  GROUP BY fdempresas_descripcion_1.numero))
        )
 SELECT a.numero,
    b.corte AS ultimo_corte,
    a.riesgo,
    a.seccion,
    a.tamano_emp,
    a.empleados_prom,
    a.suc_sucursal,
    a.departamento,
    a.municipio,
    a.mavg_prima,
    a.mavg_recaudo,
    a.derivada_recaudo AS d_recaudo,
    a.mavg_cartera_total,
    a.derivada_cartera AS d_cartera,
    a.mavg_comision,
    a.segmento,
    b.retiro
   FROM fempresas a
     LEFT JOIN corte_retiro b ON a.numero = b.numero
  WHERE a.tamano_emp::text <> ALL (ARRAY['Unipersonal'::character varying::text, 'Microempresa'::character varying::text])
WITH DATA;

ALTER TABLE public.model_query
    OWNER TO mainuser;