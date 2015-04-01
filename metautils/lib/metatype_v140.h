/*
OpenIO SDS metautils
Copyright (C) 2014 Worldine, original work as part of Redcurrant
Copyright (C) 2015 OpenIO, modified as part of OpenIO Software Defined Storage

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 3.0 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library.
*/

#ifndef OIO_SDS__metautils__lib__metatype_v140_h
# define OIO_SDS__metautils__lib__metatype_v140_h 1

#include <glib/gtypes.h>

/**
 * @defgroup metautils_chunkinfo ChunkInfo
 * @ingroup metautils_utils
 * @{
 */

/**
 * Prints a textual representation of the given chunk_info_t* in the given
 * buffer.
 *
 * The printed text will always be NULL terminated when the destination
 * buffer size is >= 1
 *
 * @param ci the chunk_id_t structure to be printed
 * @param dst the destination buffer
 * @param dstsize the size availble in the destination buffer
 *
 * @return the number of btes written or -1 in case of error
 */
gint chunk_id_to_string(const chunk_id_t * ci, gchar * dst, gsize dstsize);

/**
 * Assemble a chunk id from rawx address, volume and hexadecima id.
 */
gchar *assemble_chunk_id(const gchar *straddr, const gchar *strvol,
		const gchar *strid);

#define chunk_info_clean g_free0

/**
 * Simple function destined to be passed as a GFunc callback
 * for calls like g_slist_foreach(), etc...
 * The first argument is assumed to be a chunk_info_t*, the second
 * argument is ignored.
 *
 * @param d a pointer assumed to be a chunk_info_t* pointer that will be freed.
 * @param u ignored parameter
 */
void chunk_info_gclean(gpointer d, gpointer u);

/** @} */

/* ------------------------------------------------------------------------- */

void meta1_raw_container_clean(struct meta1_raw_container_s *raw);

void meta1_raw_container_gclean(gpointer r, gpointer ignored);

/* ------------------------------------------------------------------------- */

/**
 * @defgroup metautils_pathinfo Path Info
 * @ingroup metautils_utils
 * @{
 */

/**
 * Simple function destined to be passed as a GFunc callback
 * for calls like g_slist_foreach(), etc...
 * The first argument is assumed to be a path_info_t*, the second
 * argument is ignored.
 *
 * @param d assumed to be a pointer to a path_info_t*, freed if not NULL
 * @param u ignored
 * @see path_info_clean()
 */
void path_info_gclean(gpointer d, gpointer u);

/**
 * @brief Frees the given structure and the all its internals sub-structures
 * Accepts NULL
 * @see path_info_gclean()
 */
void path_info_clean(path_info_t * pi);

/** @} */

/* ------------------------------------------------------------------------- */

/**
 * @defgroup metautils_integrity Integrity Loop
 * @ingroup metautils_utils
 * @{
 */

/**
 * Free and clear the content of a chunk_textinfo (not the pointer itself)
 *
 * @param cti an instance of struct chunk_textinfo_s
 */
void chunk_textinfo_free_content(struct chunk_textinfo_s *cti);

/**
 * Free and clear the content of a content_textinfo (not the pointer itself)
 *
 * @param cti an instance of struct content_textinfo_s
 */
void content_textinfo_free_content(struct content_textinfo_s *cti);

/**
 * Test if the chunk given in args is the last of the chunk sequence of the given content
 *
 * @param chunk the chunk to check
 * @param content the content this chunk belongs to
 * 
 * @return 1 if the chunk is the last one, 0 otherwise
 */
int chunk_is_last(struct chunk_textinfo_s *chunk, struct content_textinfo_s *content);

/**
 * Convert a chunk info in text format to the raw format
 *
 * @param text_chunk the chunk in text format
 * @param raw_chunk the preallocated chunk in raw format
 * @param error
 *
 * @return TRUE or FALSE if an error occured (error is set)
 */
gboolean convert_chunk_text_to_raw(const struct chunk_textinfo_s* text_chunk, struct meta2_raw_chunk_s* raw_chunk, GError** error);

/**
 * Convert a chunk info in raw format to the text format
 *
 * @param raw_content a content in raw format containing the chunk to convert (and only this chunk)
 * @param text_chunk the preallocated chunk in text format
 * @param error
 *
 * @return TRUE or FALSE if an error occured (error is set)
 */
gboolean convert_chunk_raw_to_text(const struct meta2_raw_content_s* raw_content, struct chunk_textinfo_s* text_chunk, GError** error);

/**
 * Convert a content info in text format to the raw format
 *
 * @param text_content the content in text format
 * @param raw_content the preallocated content in raw format
 * @param error
 *
 * @return TRUE or FALSE if an error occured (error is set)
 */
gboolean convert_content_text_to_raw(const struct content_textinfo_s* text_content, struct meta2_raw_content_s* raw_content, GError** error);

/**
 * Convert a content info in text format to the raw format
 *
 * @param raw_content the preallocated content in raw format
 * @param text_content the content in text format
 * @param error
 *
 * @return TRUE or FALSE if an error occured (error is set)
 */
gboolean convert_content_raw_to_text(const struct meta2_raw_content_s* raw_content, struct content_textinfo_s* text_content, GError** error);

/** @} */

/* ------------------------------------------------------------------------- */

/**
 * @defgroup metautils_meta2 Meta2 
 * @ingroup metautils_utils
 * @{
 */

/**
 * Allocates a new content structure, and fills the common fields with
 * a copy of the pointed parameters
 * @deprecated
 */
struct meta2_raw_content_s *meta2_maintenance_create_content(
		const container_id_t container_id, gint64 size, guint32 nb_chunks,
		guint32 flags, const gchar * path, gsize path_len);

/**
 * prepend (order does not matter) to the list a copy of the given
 * chunk
 * @deprecated
 */
void meta2_maintenance_add_chunk(struct meta2_raw_content_s *content,
		const struct meta2_raw_chunk_s *chunk);

/**
 * Frees the memory structures : the content pointed by the argument
 * and all the chunks listed in
 * @deprecated
 */
void meta2_maintenance_destroy_content(struct meta2_raw_content_s *content);

/**
 * @deprecated
 */
void meta2_raw_content_clean(meta2_raw_content_t *content);

meta2_raw_chunk_t* meta2_raw_chunk_dup(meta2_raw_chunk_t *chunk);

void meta2_raw_chunk_clean(meta2_raw_chunk_t *chunk);

void meta2_raw_chunk_gclean(gpointer p, gpointer ignored);

gchar* meta2_raw_chunk_to_string(const meta2_raw_chunk_t *header);

struct meta2_raw_chunk_s * meta2_maintenance_create_chunk(
		const chunk_id_t * chunk_id, const chunk_hash_t hash,
		guint32 flags, gint64 size, guint32 position);

void meta2_maintenance_destroy_chunk(struct meta2_raw_chunk_s *chunk);

void meta2_property_clean(meta2_property_t *prop);

void meta2_property_gclean(gpointer prop, gpointer ignored);

void meta2_raw_content_header_clean(meta2_raw_content_header_t *content);

void meta2_raw_content_v2_clean(meta2_raw_content_v2_t *prop);

void meta2_raw_content_v2_gclean(gpointer prop, gpointer ignored);

meta2_raw_content_t* meta2_raw_content_v2_get_v1(const meta2_raw_content_v2_t *v2,
		GError **err);

/** @} */

#endif /*OIO_SDS__metautils__lib__metatype_v140_h*/
