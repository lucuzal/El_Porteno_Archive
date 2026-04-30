QUERY_CONFIGURACION_INICIAL = "SET SESSION sql_mode=(SELECT REPLACE(@@sql_mode, 'ONLY_FULL_GROUP_BY',''));"

QUERY_REGISTRO_MODIFICACIONES = "INSERT INTO registro_modificaciones (fecha, sql_query, instancia) VALUES (NOW(), %s, %s)"

QUERY_GET_LAST_ID_OPEN = """
    SELECT t.ultimo_nrev 
    FROM IDE_info t;
"""

QUERY_GET_REVISTA_POR_ID = """
    SELECT * FROM revista r 
    WHERE id=%s;
"""

QUERY_GET_STAFF_POR_ID_REVISTA = """
    SELECT p.posicion, i.nombre, i.apellido, i.genero
    FROM staff s
    INNER JOIN staff_posicion p
    ON s.staff_posicion_id = p.id
    INNER JOIN staff_integrante i
    ON s.staff_integrante_id = i.id
    WHERE s.revista_id=%s
    ORDER BY s.id;
"""

QUERY_GET_NOTAS_POR_ID_REVISTA = """
    SELECT n.id, n.revista_id, n.titulo, n.paginas, n.dossier, n.seccion, n.tipo, n.original, n.relevante, n.relevante_sexualidad, n.relevante_testimonio, n.comentarios
    FROM nota n
    WHERE n.revista_id=%s;
"""

QUERY_GET_AUTOR_DE_NOTA_POR_NOTA_ID = """
    SELECT a.id, a.nombre, a.apellido, a.genero, a.comentarios
    FROM autor a
    LEFT JOIN nota_autor na
    ON a.id = na.autor_id
    WHERE na.nota_id=%s;
"""

QUERY_GET_TEMAS_DE_NOTA_POR_NOTA_ID = """
    SELECT t.id, t.tema
    FROM tema t
    LEFT JOIN nota_tema nt
    ON t.id = nt.tema_id
    WHERE nt.nota_id=%s;
"""

QUERY_GET_CARTAS_POR_REVISTA_ID = """
    SELECT c.id, c.revista_id, c.remitente, c.tema, c.relevante
    FROM carta c
    WHERE c.revista_id=%s;
"""

QUERY_UPDATE_REVISTA_POR_ID = """
    UPDATE revista r
    SET r.tapa = %s,
        r.nota_de_tapa = %s,
        r.hexagrama = %s,
        r.paginas_faltantes =%s,
        r.formato_en_archivo = %s,
        r.comentarios = %s,
        r.precio_nominal = %s
    WHERE r.id = %s
"""

QUERY_GET_NOTA_POR_ID_NOTA = """
    SELECT n.id, n.revista_id, n.titulo, n.paginas, n.dossier, n.seccion, n.tipo, n.original, n.relevante, n.relevante_sexualidad, n.relevante_testimonio, n.comentarios
    FROM nota n
    WHERE n.id=%s; 
"""

QUERY_GET_AUTORES_POR_NOMBRE = """
    SELECT a.id, a.nombre, a.apellido, a.genero, a.comentarios
    FROM autor a
    WHERE concat(a.nombre, ' ', a.apellido) LIKE %s
    ORDER BY a.apellido;
"""

QUERY_GET_AUTOR_POR_ID_NOMBRE = """
    SELECT a.id, a.nombre, a.apellido, a.genero, a.comentarios
    FROM autor a
    WHERE a.id = %s;
"""

QUERY_GET_NOTAS_POR_AUTOR = """
        SELECT n.id, n.revista_id, n.titulo, n.paginas, n.dossier, n.seccion, n.tipo, n.original, n.relevante, n.relevante_sexualidad, n.relevante_testimonio, n.comentarios
        FROM nota n
        LEFT JOIN nota_autor na ON n.id = na.nota_id
        WHERE na.autor_id = %s
        GROUP BY n.id
        ORDER BY n.revista_id, n.paginas;
"""

QUERY_UPDATE_AUTOR = """
    UPDATE autor a
    SET a.nombre = %s,
        a.apellido = %s,
        a.genero = %s,
        a.comentarios = %s
    WHERE a.id = %s;
"""

QUERY_GET_TEMAS_POR_TEMA = """
    SELECT t.id, t.tema
    FROM tema t
    WHERE t.tema LIKE %s
    ORDER BY t.tema;
"""

QUERY_BASE_TEMAS_POR_NOTAS = """
    SELECT DISTINCT t.id, t.tema
    FROM tema t
    INNER JOIN nota_tema nt
    ON t.id = nt.tema_id
    WHERE t.tema LIKE %s AND (nt.nota_id = %s
"""

QUERY_BASE_NOTAS_POR_TEMAS = """
    SELECT n.id, n.revista_id, n.titulo, n.paginas, n.dossier, n.seccion, n.tipo, n.original, n.relevante, n.relevante_sexualidad, n.relevante_testimonio, n.comentarios
	FROM nota n
	INNER JOIN nota_tema nt ON n.id = nt.nota_id
	WHERE nt.tema_id IN (%s
"""

QUERY_GET_CATEGORIAS_POR_NOTA_ID = """
    SELECT g.id, g.grupo
    FROM grupo g
    INNER JOIN nota_grupo ng
    ON ng.grupo_id = g.id
    WHERE nota_id = %s;
"""

QUERY_GET_ARCHIVO_RESUMEN_POR_NOTA_ID = """
    SELECT a.id, a.nota_id, a.titulo, a.cuerpo_texto
    FROM analisis a
    WHERE a.nota_id = %s
    ORDER BY a.id;
"""

QUERY_GET_GRUPOS_ANALISIS = """
    SELECT g.id, g.grupo
    FROM grupo g;
"""

QUERY_AGREGAR_GRUPO_ANALISIS = """
    INSERT INTO grupo (grupo)   
    VALUES (%s);
"""

QUERY_GET_NOTAS_POR_GRUPO_ANALISIS = """
    SELECT n.id, n.revista_id, n.titulo, n.paginas, n.dossier, n.seccion, n.tipo, n.original, n.relevante, n.relevante_sexualidad, n.relevante_testimonio, n.comentarios
	FROM nota n
	INNER JOIN nota_grupo ng ON n.id = ng.nota_id
	WHERE ng.grupo_id = %s
	ORDER BY n.revista_id;
"""

QUERY_GET_CARTAS_POR_GRUPO_ANALISIS = """
    SELECT c.id, c.revista_id, c.remitente, c.tema, c.relevante
	FROM carta c
	INNER JOIN carta_grupo cg ON c.id = cg.carta_id
	WHERE cg.grupo_id = %s
	ORDER BY c.revista_id;
"""

QUERY_CARGAR_NOTA_AL_GRUPO_ANALISIS = """
    INSERT INTO nota_grupo (nota_id, grupo_id)
    VALUES (%s, %s);
"""

QUERY_DELETE_NOTA_DE_GRUPO_DE_ANALISIS = """
    DELETE FROM nota_grupo ng
    WHERE ng.nota_id = %s and ng.grupo_id = %s;
"""

QUERY_AGREGAR_ARCHIVO_RESUMEN = """
    INSERT INTO analisis (nota_id, cuerpo_texto, titulo)
    VALUES (%s, %s, %s);
"""

QUERY_AGREGAR_ARCHIVO_RESUMEN_CARTA = """
    INSERT INTO analisis_carta (carta_id, cuerpo_texto, titulo)
    VALUES (%s, %s, %s)
"""

QUERY_MODIFICAR_ARCHIVO_RESUMEN = """
    UPDATE analisis a
    SET a.cuerpo_texto = %s,
        a.titulo = %s
    WHERE a.id = %s;
"""

QUERY_MODIFICAR_ARCHIVO_RESUMEN_CARTA = """
    UPDATE analisis_carta ac
    SET ac.cuerpo_texto = %s,
        ac.titulo = %s
    WHERE ac.id = %s
"""

QUERY_GET_ARCHIVO_RESUMEN = """
    SELECT a.id, a.nota_id, a.cuerpo_texto, a.titulo
    FROM analisis a
    WHERE a.id = %s;
"""

QUERY_DELETE_ARCHIVO_RESUMEN = """
    DELETE FROM analisis a
    WHERE a.id = %s;
"""

QUERY_ACTUALIZAR_TITULO = """
    UPDATE analisis a
    SET a.titulo = %s
    WHERE a.id = %s;
"""

QUERY_GET_ARCHIVO_RESUMEN_CARTA_POR_ID_CARTA = """
    SELECT ac.id, ac.carta_id, ac.cuerpo_texto, ac.titulo
    FROM analisis_carta ac
    WHERE ac.carta_id = %s;
"""

QUERY_GET_ARCHIVO_RESUMEN_CARTA_POR_ID = """
    SELECT ac.id, ac.carta_id, ac.cuerpo_texto, ac.titulo
    FROM analisis_carta ac
    WHERE ac.id = %s;
"""

QUERY_DELETE_ARCHIVO_RESUMEN_CARTA = """
    DELETE FROM analisis_carta ac
    WHERE ac.id = %s;
"""

QUERY_DELETE_CARTA_DE_GRUPO_ANALISIS = """
    DELETE FROM carta_grupo cg
    WHERE cg.carta_id = %s AND
          cg.grupo_id = %s;
"""

QUERY_ACTUALIZAR_TITULO_ARCHIVO_RESUMEN_CARTA = """
    UPDATE analisis_carta ac
    SET ac.titulo = %s
    WHERE ac.id = %s;
"""

QUERY_GET_GRUPOS_ANALISIS_PARA_CARTA = """
    SELECT g.id, g.grupo
    FROM grupo g
    INNER JOIN carta_grupo cg ON g.id = cg.grupo_id
    WHERE cg.carta_id = %s;
"""

QUERY_GUARDAR_NUEVA_CARTA = """
    INSERT INTO carta (revista_id, remitente, tema, relevante)
    VALUES (%s, %s, %s, %s);
"""

QUERY_UPDATE_CARTA = """
    UPDATE carta c
    SET c.remitente = %s,
        c.tema = %s,
        c.relevante = %s
    WHERE c.id = %s;
"""

QUERY_ADD_CARTA_A_GRUPO_ANALISIS = """
    INSERT INTO carta_grupo (carta_id, grupo_id)
    VALUES (%s, %s);
"""

QUERY_GET_AUTORES_POR_REVISTA = """
    SELECT a.id, a.nombre, a.apellido, a.genero, a.comentarios, na.nota_id 
    FROM autor a
    JOIN nota_autor na ON na.autor_id = a.id
    JOIN nota n ON n.id = na.nota_id
    WHERE n.revista_id = %s;
"""

QUERY_GET_TEMAS_POR_REVISTA = """
    SELECT t.id, t.tema, nt.nota_id
    FROM tema t
    JOIN nota_tema nt ON nt.tema_id = t.id
    JOIN nota n ON n.id = nt.nota_id
    WHERE n.revista_id = %s;
"""

QUERY_GET_GRUPO_ANALISIS_POR_REVISTA = """
    SELECT g.id, g.grupo, ng.nota_id
    FROM grupo g
    JOIN nota_grupo ng ON ng.grupo_id = g.id
    JOIN nota n ON n.id = ng.nota_id
    WHERE n.revista_id = %s;
"""

QUERY_GET_ARCHIVO_REVISTA_POR_REVISTA = """
    SELECT a.id, a.nota_id, a.cuerpo_texto, a.titulo
    FROM analisis a
    JOIN nota n ON n.id = a.nota_id
    WHERE n.revista_id = %s;
"""