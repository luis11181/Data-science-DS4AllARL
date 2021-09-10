-- FUNCTION: public.make_fempresastable()

-- DROP FUNCTION public.make_fempresastable();

CREATE OR REPLACE FUNCTION public.make_fempresastable(
	)
    RETURNS character varying
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE 

    resumen RECORD;
	i_meses_inactivo integer; --contador 
    r_avgprima4 numeric;
	 r_avg_recaudo_mes4 numeric; 
     r_avgcomision4  numeric;
	 r_avgcartera_total4  numeric;
	 ha_retirado_multiplesveces varchar(15);
	 derivada_recaudo1 numeric;
	 derivada_cartera1 numeric;
	 derivada_recaudo2 numeric;
	 derivada_cartera2 numeric;
	 derivada_recaudo3 numeric;
	 derivada_cartera3 numeric;
	 derivada_recaudo numeric;
	 derivada_cartera numeric;
		
BEGIN 
	
	
	------------------------------------------
	-- query PARA CREAR  los average y average al final
	
	--SELECT avg(prima) as ravgprima FROM
   --(SELECT cap_cs137 FROM capintec ORDER BY cap_date DESC LIMIT 20);
   
   --RAISE NOTICE 'paso 1';   
		
	for resumen in (
	SELECT 
		numero,
		MAX(corte) as maxcorte, 
		AVG(prima) as avgprima, 
		AVG(recaudo_mes) as avg_recaudo_mes, 
		AVG(comision) as avgcomision, 
		AVG(cartera_total) as avgcartera_total, 
		SUM(retiro) AS tr
		FROM fdempresas_descripcion  
		where not exists (
		select from fempresas i
			where i.numero=fdempresas_descripcion.numero
		)
	GROUP BY numero
	) loop

		----------------------------------------------------------------		
		-- añadir el valor de las medias ultimos 4 meses a la tabla temporal 
		SELECT 
			avg(d.prima) as r_avgprima4,
			avg(d.recaudo_mes) as r_avg_recaudo_mes4, 
			avg(d.comision) as r_avgcomision4, 
			avg(d.cartera_total) as r_avgcartera_total4
		 into 
			 r_avgprima4,
			 r_avg_recaudo_mes4 ,
			 r_avgcomision4  ,
			 r_avgcartera_total4 
		FROM  
		  fdempresas_descripcion as d
		WHERE 
		d.numero=resumen.numero
		and d.corte > (resumen.maxcorte - (interval '1 month' *4))::date;
		
		
		
----------------------------------------------------------------		
		-- derivada manual de los ultimos 3 meses
		-- mes mas reciente, mes 3 desde el ultimo
		SELECT 
			d.recaudo_mes as recaudomes, 
			d.cartera_total as carterames
		 into 
			 derivada_recaudo1,
			 derivada_cartera1
		FROM  
		  fdempresas_descripcion as d
		WHERE 
		d.numero=resumen.numero
		and d.corte-(resumen.maxcorte - (interval '1 month' *1))::date 
		between	-10 and 10;
		
		
		-- derivada manual de los ultimos 3 meses
		-- segundo mes mas reciente, mes 4 desde el ultimo
		SELECT 
			d.recaudo_mes as recaudomes, 
			d.cartera_total as carterames
		 into 
			 derivada_recaudo2,
			 derivada_cartera2
		FROM  
		  fdempresas_descripcion as d
		WHERE 
		d.numero=resumen.numero
		and d.corte-(resumen.maxcorte - (interval '1 month' *2))::date 
		between	-10 and 10;
		
		
		-- derivada manual de los ultimos 3 meses
		-- segundo mes mas reciente, mes 4 desde el ultimo
		SELECT 
			d.recaudo_mes as recaudomes, 
			d.cartera_total as carterames
		 into 
			 derivada_recaudo3,
			 derivada_cartera3
		FROM  
		  fdempresas_descripcion as d
		WHERE 
		d.numero=resumen.numero
		and d.corte -(resumen.maxcorte - (interval '1 month' *3))::date 
		between	-6 and 6;
		
		
		--derivada total
		
		derivada_recaudo := -1* (3 * derivada_recaudo3/2) + (2 *  derivada_recaudo2) -1*(derivada_recaudo1/2);
		
	    derivada_recaudo := coalesce(derivada_recaudo,0);
		
		derivada_cartera := -1*(3 * derivada_cartera3/2) + (2 *  derivada_cartera2) -1 *  (derivada_cartera1/2);

		derivada_cartera := coalesce(derivada_cartera,0);

		--RAISE NOTICE 'fecha empresa';

		-- añadir el valor de si se ha retirado multiples veces a la tabla temporal
		ha_retirado_multiplesveces:=
			 case when resumen.tr > 3 then 'si'
			  when resumen.tr < 3 then 'no'
			  else 'medio' 
			  end; 

		INSERT INTO fempresas (
		numero ,
		ultimo_corte ,
		corte_evaluado ,
		num_registros ,
		ciiu ,
		riesgo ,
		seccion ,
		descripcion_seccion ,
		tamano_emp ,
		empleados_prom ,
		suc_sucursal ,
		departamento ,
		municipio ,
		divipola ,
		lat ,
		lon ,
		avg_prima ,
		mavg_prima ,
		avg_recaudo ,
		mavg_recaudo ,
		avg_cartera_total ,
		mavg_cartera_total ,
		avg_comision ,
		mavg_comision ,
		ha_retirado_multiplesveces,
		segmento,
		derivada_recaudo,
		derivada_cartera)
		SELECT 
			e.numero, 
			resumen.maxcorte, 
			resumen.maxcorte,
			e.num_registros, 
			e.ciiu, 
			e.riesgo, 
			e.seccion, 
			e.descripcion_seccion, 
			e.tamano_emp,
			e.empleados_prom, 
			e.suc_sucursal,  
			e.departamento, 
			e.municipio, 
			e.divipola , 
			e.lat , 
			e.lon, 
			resumen.avgprima, 
			r_avgprima4, 
			resumen.avg_recaudo_mes, 
			r_avg_recaudo_mes4, 
			resumen.avgcartera_total, 
			r_avgcartera_total4, 
			resumen.avgcomision, 
			r_avgcomision4, 
			ha_retirado_multiplesveces,
			e.segmento,
			derivada_recaudo,
			derivada_cartera
		FROM empresas as e
		where e.numero=resumen.numero;	
	end loop;
	
	------------------------------------------
	--return final de la funcion
	RETURN 'success';
	EXCEPTION WHEN OTHERS THEN    
	RETURN SQLERRM ;-- SI NO FUNCION RETORNA MENSAJE DE ERROR
END;

/*
-- añadir y update un campo segmento a la  tabla empresas
		WITH temp_table AS
	    (
		SELECT t.numero, t.corte, d.segmento
		from (select max(corte) as corte, numero
		 FROM dempresas_descripcion 
		 GROUP BY numero) as t, dempresas_descripcion as d
		 WHERE t.numero = d.numero AND t.corte = d.corte 
		 )
		
		UPDATE empresas
    	SET segmento = d.segmento	
		FROM temp_table as d
   	    WHERE d.numero = empresas.numero ;

*/

/* falta arreglar bien el campo retiros, incluyendo los meses inactivo,
toca eliminar los registros despues de qe la empresa se retire si esta no se vuelve a afiliar
agregar retiros oficiales
*/

--DELETE FROM fempresas;
--SELECT make_fempresastable();
$BODY$;

ALTER FUNCTION public.make_fempresastable()
    OWNER TO mainuser;
