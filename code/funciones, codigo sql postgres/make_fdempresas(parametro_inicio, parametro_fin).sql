-- FUNCTION: public.make_fdempresas(numeric, numeric)

-- DROP FUNCTION public.make_fdempresas(numeric, numeric);

CREATE OR REPLACE FUNCTION public.make_fdempresas(
	parameter_inicio numeric,
	parameter_fin numeric)
    RETURNS character varying
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE 
	recordImprimir RECORD; 
	recordEmpresa RECORD;
	recordDescripcion RECORD;
    recordDescripcion_mes_anterior RECORD;
	tempCorte date;
	tempCorteAnterior date;
	esInicial boolean; 
	vciclo_sin_registro numeric;
	vciclo_recaudo_cero numeric;
	recaudo numeric;
	tuvo_retiro boolean;
	este_mes_tiene_recaudo_cero integer;
	i_meses_inactivo integer; --contador pada saber a cuantos meses ponerle 3 en retiro, es decir inactivo
	vd_ultimo_retiro date;
BEGIN 

	for recordEmpresa in (
		select * 
		from empresas
		where empresas.numero >= parameter_inicio AND empresas.numero <= parameter_fin
		ORDER BY NUMERO
	) 		
		loop		
			RAISE NOTICE 'Ciclo 1= %', recordEmpresa.numero;
		esInicial := true;
					
		for recordDescripcion in (
			--trae cada row por mes, seleccionando el registro mensual con mayor recaudo
			select DISTINCT ON (corte_recortado) corte_recortado, 
			idx, corte, actividad_economica, suc_sucursal, ese_descripcion, segmento, prima, pyp, comision, g_admin, f_arl, soa_cont, matematica_cont, mesada_pensional, soa_pro_cont, soa_ocurr, matematica_ocurr, rt_cont, rt_ocurr, cartera_total, cartera_vencida, fecha_corte, relaciones_laborales, anio, mes, tamano_emp, recaudo_del_mes, at_del_mes, ep_del_mes, mortal, numero
			from  (select TO_DATE(to_char(corte,'yyyymm'),'YYYYMM') AS corte_recortado, 
					t.idx,
					t.corte,
					t.actividad_economica,
					t.suc_sucursal,
					t.ese_descripcion,
					t.segmento,
					t.prima,
					t.pyp,
					t.comision,
					t.g_admin,
					t.f_arl,
					t.soa_cont,
					t.matematica_cont,
					t.mesada_pensional,
					t.soa_pro_cont,
					t.soa_ocurr,
					t.matematica_ocurr,
					t.rt_cont,
					t.rt_ocurr,
					t.cartera_total,
					t.cartera_vencida,
					t.fecha_corte,
					t.relaciones_laborales,
					t.anio,
					t.mes,
					t.tamano_emp,
					t.recaudo_del_mes,
					t.at_del_mes,
					t.ep_del_mes,
					t.mortal,
					t.numero				   
				   from dempresas_descripcion t
				  where t.numero=recordEmpresa.numero
				  ) AS descripcion
			where descripcion.numero=recordEmpresa.numero
			order by 
			 corte_recortado 
			-- ,descripcion.recaudo_del_mes DESC NULLS LAST
		)			
		--Which row in that group for the distinct on is returned is specified with the ORDER BY clause
		-- null last hace que estos valores se tomen como menores, y por lo tanto no se escoja si hay uno mayor en ese mismo mes
			loop

				tempCorte := recordDescripcion.corte_recortado;--TO_DATE(to_char(recordDescripcion.corte,'yyyymm'),'YYYYMM');
				--RAISE NOTICE 'Ciclo 2= %', tempCorte;
				
				-- en el primer ciclo de una empresa le asigna el corte del mes anterior igual a un mes antes pues este no exitia
				-- se inicializan los contadores al ser el primer ciclo
				if ( esInicial) then
					
					tempCorteAnterior:=(tempCorte- '1 month'::interval)::date;
					
					vciclo_recaudo_cero := 0;
					vciclo_sin_registro :=0;
					tuvo_retiro := false;
					recordDescripcion_mes_anterior := recordDescripcion;
					vd_ultimo_retiro :=null;
				end if;
				
				
				------------------------------------------
				-- crear los campos retiro para empresas inactivas, 3. entra si un recaudo es mayor a cero y tuvo un retiro antes
				if (recordDescripcion.recaudo_del_mes>0 AND tuvo_retiro) then
					UPDATE fdempresas_descripcion as e
					SET retiro = 3
					WHERE (
					corte >= (vd_ultimo_retiro +(interval '1 day' ))::date
					AND  corte <= (tempCorte -(interval '1 day' ))::date   
					AND  recaudo_mes=0 
					and e.numero=recordEmpresa.numero
					);

				end if;
				
				
				------------------------------------------
				-- limpiar los valores nulos y negativos de recaudo mes, y decir cuantos meses seguidos se tiene recaudo 0
				if (recordDescripcion.recaudo_del_mes>0 AND recordDescripcion.recaudo_del_mes IS NOT NULL) then
					recaudo := floor(recordDescripcion.recaudo_del_mes);
					vciclo_recaudo_cero := 0;
					este_mes_tiene_recaudo_cero := 0;
					tuvo_retiro:= false;
					vciclo_sin_registro:=0; --cantidad de ciclos sin registros hasta encontrar un registro en la tabla con recaudo mayor a cero
				else
				    recaudo := 0;
					vciclo_recaudo_cero := vciclo_recaudo_cero+1;
					este_mes_tiene_recaudo_cero := 1;
				end if;
				
				------------------------------------------
				-- si la resta del mes anterior y el actual es mayor a 33 dias entra y llena los meses faltantes
				if (tempCorte - tempCorteAnterior > 33 ) then
				   --RAISE NOTICE 'Entro en paso 1 faltan meses por rellenar';
					
					while (tempCorte - tempCorteAnterior) > 33
						loop
				         --RAISE NOTICE 'Entro en loop paso 1';
						  
						  begin
						  INSERT INTO fdempresas_descripcion (
							numero,
							corte,
							prima,
							recaudo_mes,
							AVG_ultimos_recaudo_mes,
							retiro ,
							pyp ,
							comision ,
							g_admin ,
							soa_cont ,
							mesada_pensional ,
							soa_pro_cont ,
							soa_ocurr ,
							cartera_total ,
							cartera_vencida ,
							relaciones_laborales ,
							at_del_mes ,
							ep_del_mes ,
							mortal)
							VALUES(
								recordDescripcion.numero,
								(tempCorteAnterior +(interval '1 month' ))::date,
								recordDescripcion_mes_anterior.prima,
								0 ,--pone recaudo cero en el mes que no aparece la empresa
								0 ,-- average 
								0 ,-- retiro
								recordDescripcion_mes_anterior.pyp ,
								recordDescripcion_mes_anterior.comision ,
								recordDescripcion_mes_anterior.g_admin ,
								recordDescripcion_mes_anterior.soa_cont ,
								recordDescripcion_mes_anterior.mesada_pensional ,
								recordDescripcion_mes_anterior.soa_pro_cont ,
								recordDescripcion_mes_anterior.soa_ocurr ,
								recordDescripcion_mes_anterior.cartera_total ,
								recordDescripcion_mes_anterior.cartera_vencida ,
								recordDescripcion_mes_anterior.relaciones_laborales ,
								0 ,
								0 ,
								0);
								
							EXCEPTION
							  WHEN others THEN
								--RAISE NOTICE 'ERROR EN INSERCIN ' ;
							END;
						  
						  tempCorteAnterior:= (tempCorteAnterior+ '1 month'::interval)::date;  			  
						  vciclo_sin_registro := vciclo_sin_registro+1;
						  
						end loop;
				end if;
				
				------------------------------------------
				-- debe ir aca para no resetear el contador de meses sin registros		
				-- arreglar los valores del campo retiro si hay 6+ meses en recaudo cero
				--RAISE NOTICE 'INDICES, NUMERO DE MESES SIN REGISTRO:% , NUMERO DE MESES RECAUDO CERO:% ', vciclo_sin_registro,vciclo_recaudo_cero;
				if (vciclo_sin_registro+vciclo_recaudo_cero>=6) then
				
			        --RAISE NOTICE 'Entro a crear indices de retiro informal, NUMERO DE MESES SIN REGISTRO:% , NUMERO DE MESES RECAUDO CERO:% ', vciclo_sin_registro,vciclo_recaudo_cero;
				
					UPDATE fdempresas_descripcion
					SET retiro = 2 
					WHERE (numero = recordDescripcion.numero 
						   AND corte = (tempCorte - (interval '1 month' *(vciclo_sin_registro+vciclo_recaudo_cero+1-este_mes_tiene_recaudo_cero)))::date
						   )
						   ;--corte sea igual al primer dia que se desafilio
					
					vd_ultimo_retiro:=	((tempCorte - (interval '1 month' *(vciclo_sin_registro+vciclo_recaudo_cero+1-este_mes_tiene_recaudo_cero)))::date);
					
					tuvo_retiro:= true;
				end if;

				------------------------------------------		
			    -- si el primer mes existente o los meses son consecutivos	
				if (tempCorte - tempCorteAnterior >26 AND tempCorte - tempCorteAnterior <33 )then
				
			    	--RAISE NOTICE 'Entro en paso 3, MESES consecutivos en registro';
				
					INSERT INTO fdempresas_descripcion (
					numero,
					corte,
					prima,
					recaudo_mes,
					AVG_ultimos_recaudo_mes,
					retiro ,
					pyp ,
					comision ,
					g_admin ,
					soa_cont ,
					mesada_pensional ,
					soa_pro_cont ,
					soa_ocurr ,
					cartera_total ,
					cartera_vencida,
					relaciones_laborales ,
					at_del_mes ,
					ep_del_mes ,
					mortal)
					VALUES(
						recordDescripcion.numero,
						tempCorte,
						recordDescripcion.prima,
						recaudo,
						--round(AVG(recordDescripcion.recaudo_del_mes)OVER(ROWS BETWEEN 4 PRECEDING AND CURRENT ROW),2)
						0, --arreglar, va el rolling average
						0,-- falta arreglar
						recordDescripcion.pyp ,
						recordDescripcion.comision ,
						recordDescripcion.g_admin ,
						recordDescripcion.soa_cont ,
						recordDescripcion.mesada_pensional ,
						recordDescripcion.soa_pro_cont ,
						recordDescripcion.soa_ocurr ,
						recordDescripcion.cartera_total ,
						recordDescripcion.cartera_vencida ,
						recordDescripcion.relaciones_laborales ,
						recordDescripcion.at_del_mes ,
						recordDescripcion.ep_del_mes ,
						recordDescripcion.mortal
						);
				
				-- si se repiten dos o mas registros para ese mes no hace nada y omite, no deberian haber registros de fecha menor
				end if;

				tempCorteAnterior:=tempCorte;	
				recordDescripcion_mes_anterior := recordDescripcion;
				esInicial := false;
			
			------------------------------------------ end inner loop
			end loop;
		
		
		
		------------------------------------------
		-- eliminar los registros en ceros despues de un retiro informal de la empresa y no mas actividad futura
		select 
		max(corte)
		into vd_ultimo_retiro
		from 
		fdempresas_descripcion AS e
		where numero=recordEmpresa.numero
		AND e.retiro = 2
		AND NOT EXISTS (SELECT 'x'
					   FROM fdempresas_descripcion as i
					   WHERE i.numero =e.numero
					   AND i.corte > e.corte
					   AND i.recaudo_mes >0) ;
		
	    if vd_ultimo_retiro IS NOT NULL then
	   
		   delete from fdempresas_descripcion 
		   where recaudo_mes=0
		   AND corte > vd_ultimo_retiro
		   and numero=recordEmpresa.numero;
		end if;
		
		
        -- ------------------ fin loop externo empresas
		end loop;
		
		
		------------------------------------------
		-- query aparte para hacer el update y crear las medias moviles pudiendo usar las window que no se permitian antes
		WITH temp_table AS
		(
		SELECT round(AVG(recaudo_mes) OVER( PARTITION BY numero 
										  ORDER BY corte ASC
										  ROWS BETWEEN 4 PRECEDING AND CURRENT ROW 
										  ),2) AS ravg, numero, corte
		FROM fdempresas_descripcion)
		
		UPDATE fdempresas_descripcion
		SET AVG_ultimos_recaudo_mes = temp_table.ravg
		FROM temp_table
		WHERE fdempresas_descripcion.numero = temp_table.numero 
			AND fdempresas_descripcion.corte = temp_table.corte;
		
		------------------------------------------
		-- agregar retiro formal a los que competa
		UPDATE fdempresas_descripcion
    	SET retiro = 1	
		FROM dempresas_retiradas
   	    WHERE fdempresas_descripcion.numero = dempresas_retiradas.numero
			  AND dempresas_retiradas.tipo_retiro = 'RETIRO EMPLEADOR - APROBADO'
			  AND TO_DATE(to_char(dempresas_retiradas.vigencia_hasta,'yyyymm'),'YYYYMM') = fdempresas_descripcion.corte  ;

		---------------------------
		-- Quitar empresas sin historial de recaudo

		WITH no_recaudo AS (
			SELECT numero
			FROM fdempresas_descripcion
			GROUP BY numero
			HAVING SUM(recaudo_mes) < 1
		)
		DELETE FROM fdempresas_descripcion
		USING no_recaudo
		WHERE fdempresas_descripcion.numero = no_recaudo.numero;
		
		
		---------------------------
		-- agregar retiro informal '2' a empresas que llevan seis meses desde marzo de 2021 sin aparecer

		WITH sin_6_meses AS (
			SELECT numero,
			MAX(corte) as maxcorte
			FROM fdempresas_descripcion
			GROUP BY numero
			HAVING MAX(corte) < (to_date('2021-03-15','yyyy-mm-dd') - interval '1 month' * 6)::date
		)
		UPDATE fdempresas_descripcion
    	SET retiro = 2
		FROM sin_6_meses
   	    WHERE fdempresas_descripcion.numero = sin_6_meses.numero AND 
		      fdempresas_descripcion.corte = sin_6_meses.maxcorte AND
			  fdempresas_descripcion.retiro NOT IN (1,2);

		
        ------------------------------------------
        --return final de la funcion
		RETURN 'success';
		EXCEPTION WHEN OTHERS THEN    
	    RETURN SQLERRM ;-- SI NO FUNCION RETORNA MENSAJE DE ERROR
END;

/* 
toca eliminar los registros despues de que la empresa se retire si esta no se vuelve a afiliar
*/
--TRUNCATE Fdempresas_descripcion;
--DELETE FROM Fdempresas_descripcion;
--SELECT make_fdempresas(1,100);
--SELECT make_fdempresas(101,1000);
--SELECT make_fdempresas();
$BODY$;

ALTER FUNCTION public.make_fdempresas(numeric, numeric)
    OWNER TO mainuser;
