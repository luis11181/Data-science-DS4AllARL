-- View: public.queryGraficasDescriptivas

-- DROP MATERIALIZED VIEW public."queryGraficasDescriptivas";

CREATE MATERIALIZED VIEW public."queryGraficasDescriptivas"
TABLESPACE pg_default
AS
 SELECT e.descripcion_seccion,
    e.tamano_emp,
    lpad(floor((e.divipola / 1000)::double precision)::text, 2, '0'::text) AS divipola,
    avg(e.avg_prima) AS avg_prima,
    avg(e.avg_recaudo) AS avg_recaudo,
    e.segmento,
    d.corte,
    d.retiro,
    e.departamento,
    count(*) AS ocurrencias
   FROM fempresas e
     JOIN fdempresas_descripcion d ON e.numero = d.numero
  WHERE e.tamano_emp::text <> 'Unipersonal'::text
  GROUP BY e.descripcion_seccion, e.tamano_emp, (floor((e.divipola / 1000)::double precision)), e.departamento, e.segmento, d.corte, d.retiro
  ORDER BY d.corte
WITH DATA;

ALTER TABLE public."queryGraficasDescriptivas"
    OWNER TO mainuser;