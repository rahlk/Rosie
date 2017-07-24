#include "radix_tree.h"
#include <stdlib.h>
#include <stdio.h>

#define RT_BRANCH_FACTOR_BIT		(6)
#define RT_BRANCH_FACTOR			(1 << RT_BRANCH_FACTOR_BIT)
#define RT_BRANCH_FACTOR_MASK		(RT_BRANCH_FACTOR - 1)
#define RT_MAX_HEIGHT				(11)	//  div_round_up (64, 6)

int initialized = 0;
int max_height;
static unsigned long max_index [RT_MAX_HEIGHT];

struct radix_node {
	unsigned int height;
	unsigned int offset;				// for shrinking
	unsigned int child_count;
	union {
		struct radix_node *parent;
		struct list_head head;			// for radix tree deletion
	};
	struct radix_node *slots [RT_BRANCH_FACTOR];
};

static inline long div_round_up (long n, long d) {
	long tmp = n + d - 1;
	return tmp / d;
}

static inline void initialize_max_index (void) {
	max_height = (int) div_round_up (sizeof (unsigned long) << 3, RT_BRANCH_FACTOR_BIT);
	int i;
	unsigned long last = 1;
	//puts ("max index -----");
	for (i = 0; i < max_height; ++i) {
		max_index[i] = last << RT_BRANCH_FACTOR_BIT;
		last = max_index[i];
		--max_index[i];
		//printf ("%lu\n", max_index[i]);
	}
}

static inline struct radix_data_node * new_radix_data_node (unsigned long key, void *data) {
	struct radix_data_node *retval = (struct radix_data_node*) malloc (sizeof (struct radix_data_node));
	if (retval == NULL)
		return NULL;

	retval->key = key;
	retval->data = data;
	INIT_LIST_HEAD (&retval->iter_head);
	return retval;
}

static inline struct radix_node * new_radix_node (struct radix_node *parent,
		unsigned int height,
		unsigned int offset) {
	struct radix_node *retval = (struct radix_node*) malloc (sizeof (struct radix_node));
	if (retval == NULL)
		return NULL;

	int i;
	struct radix_node **slots = retval->slots;
	for (i = 0; i < RT_BRANCH_FACTOR; ++i)
		slots[i] = NULL;

	retval->height = height;
	retval->offset = offset;
	retval->child_count = 0;
	retval->parent = parent;
	return retval;
}

struct radix_tree * new_radix_tree () {
	struct radix_tree *retval = (struct radix_tree*) malloc (sizeof (struct radix_tree));
	if (retval == NULL)
		return NULL;

	if (!initialized) {
		initialize_max_index ();
		initialized = 1;
	}

	retval->size = 0;
	retval->root = new_radix_node (NULL, 0, 0);
	INIT_LIST_HEAD (&retval->head);
	if (retval->root == NULL) {
		free (retval);
		retval = NULL;
	}
	return retval;
}

static inline void delete_radix_data_node (struct radix_data_node *data) {
	list_del (&data->iter_head);
	free (data);
}

static inline void delete_radix_node (struct radix_node *node) {
	free (node);
}

// BFS delete, no recursion
void delete_radix_tree (struct radix_tree * tree) {
	struct radix_node * node, *slot, **slots;
	struct list_head rhead = LIST_HEAD_INIT (rhead);
	int i;

	node = tree->root;

	// empty tree, don't traverse
	if (node == NULL)
		goto out_skip_traversal;

	// enqueue root node
	list_add_tail (&node->head, &rhead);

	// while queue is not empty
	while (rhead.next != &rhead) {
		// pop head
		node = container_of (rhead.next, struct radix_node, head);
		list_del (&node->head);
		slots = node->slots;
		if (node->height > 0) {
			for (i = 0, slot = slots[i];
					i < RT_BRANCH_FACTOR;
					++i, slot = slots[i])
				if (slot) {
					list_add_tail (&slot->head, &rhead);
				}
		} else if (node->height == 0) {
			// if node->height == 0 -> children are data node, free the struct
			for (i = 0, slot = slots[i];
					i < RT_BRANCH_FACTOR;
					++i, slot = slots[i])
				if (slot) {
					free (slot);
				}
		} // else { TODO: dump some shits to debug this damn thing; }
		free (node);
	}

out_skip_traversal:
	free (tree);
}

static inline struct radix_node * _rt_extend (struct radix_node *root) {
	struct radix_node *retval = new_radix_node (NULL, root->height + 1, 0);
	if (retval == NULL)
		return NULL;
	retval->slots[0] = root;
	++retval->child_count;
	root->parent = retval;
	return retval;
}

/**
 * shrink the tree from the leaf nodes
 */
static inline void _rt_shrink_node (struct radix_node *node) {
	struct radix_node *parent;
	/**
	 * Only shrink radix node without children
	 */
	while (node->child_count == 0) {
		parent = node->parent;
		if (parent == NULL)
			return;
		parent->slots[node->offset] = NULL;
		--parent->child_count;
		delete_radix_node (node);
		node = parent;
	}
}

/**
 * reduce tree height by shrinking from the root node
 */
static inline void _rt_shrink_tree (struct radix_tree *tree) {
	struct radix_node *rnode = tree->root;
	/**
	 * 1. Only shrink non-leaf root
	 * 2. Don't shrink branching root
	 * 3. Only shrink when root acts as zero prefix
	 */
	while (rnode->height > 0 &&
			rnode->child_count == 1 &&
			rnode->slots[0] != NULL)
	{
		tree->root = rnode->slots[0];
		delete_radix_node (rnode);
		rnode = tree->root;
	}
}


void * radix_tree_insert (struct radix_tree *tree, unsigned long key, void *data) {
	void * retval = NULL;
	struct radix_data_node *dnode;
	struct radix_node *parent, *slot, **slots;
	register unsigned int height, index, shift;

	slot = tree->root;
	while (key > max_index[slot->height]) {
		slot = _rt_extend (slot);
		if (slot == NULL) {
			// TODO: Why ??? No memory ???
			puts ("no memory");
			goto out_error_extend;
		}
		tree->root = slot;
	}

	parent = tree->root;
	slot = NULL;
	slots = parent->slots;
	height = parent->height;
	shift = height * RT_BRANCH_FACTOR_BIT;

	while (height > 0) {
		index = (key >> shift) & RT_BRANCH_FACTOR_MASK;
		slot = slots[index];
		if (slot == NULL) {
			// grow slot
			slot = new_radix_node (parent, height - 1, index);
			if (slot == NULL) {
				// TODO: Fuck the memory problem
				puts ("no memory");
				goto out_error;
			} else {
				slots[index] = slot;
				++parent->child_count;
			}
		}

		// move down a level;
		slots = slot->slots;
		parent = slot;
		shift -= RT_BRANCH_FACTOR_BIT;
		--height;
	}

	index = key & RT_BRANCH_FACTOR_MASK;
	if (slots[index] == NULL) { // insert if not exist
		dnode = new_radix_data_node (key, data);
		if (dnode == NULL) {
			// TODO: Fuck the memory problem
			puts ("no memory");
			goto out_error;
		} else {
			++parent->child_count;
			++tree->size;

			slots[index] = (struct radix_node*) dnode;
			list_add_tail (&dnode->iter_head, &tree->head);
		}
	}
	retval = slots[index];

out:
	return retval;

out_error:
	_rt_shrink_node (parent);

out_error_extend:
	_rt_shrink_tree (tree);
	retval = NULL;
	goto out;
}

static inline struct radix_node * _rt_find_slot (struct radix_tree *tree, unsigned long key) {
	struct radix_node *retval = NULL;
	struct radix_node *slot, **slots;
	register unsigned int height, index, shift;

	if (key > max_index[tree->root->height])
		goto out;

	slot = tree->root;
	slots = slot->slots;
	height = slot->height;
	shift = height * RT_BRANCH_FACTOR_BIT;

	while (height > 0) {
		index = (key >> shift) & RT_BRANCH_FACTOR_MASK;
		slot = slots[index];
		if (slot == NULL)
			goto out;
		slots = slot->slots;
		shift -= RT_BRANCH_FACTOR_BIT;
		--height;
	}

	retval = slot;

out:
	return retval;
}

struct radix_data_node * radix_tree_find (struct radix_tree *tree, unsigned long key) {
	struct radix_data_node *retval = NULL;
	struct radix_node *slot;
	unsigned int index;

	slot = _rt_find_slot (tree, key);
	if (slot == NULL)
		goto out;

	index = key & RT_BRANCH_FACTOR_MASK;
	retval = (struct radix_data_node *) slot->slots[index];

out:
	return retval;
}
// return the data associated with the key
void * radix_tree_delete (struct radix_tree *tree, unsigned long key) {
	void * retval = NULL;
	unsigned int index;
	struct radix_data_node *dnode;
	struct radix_node *slot = _rt_find_slot (tree, key);
	if (slot == NULL)
		goto out;

	index = key & RT_BRANCH_FACTOR_MASK;
	dnode = (struct radix_data_node *) slot->slots[index];
	if (dnode == NULL)
		goto out;

	retval = dnode->data;
	delete_radix_data_node (dnode);
	slot->slots[index] = NULL;
	--slot->child_count;
	_rt_shrink_node (slot);
	_rt_shrink_tree (tree);

out:
	return retval;
}

// DFS radix tree dump
void radix_tree_dfs_dump (struct radix_node *node, unsigned long prefix) {
	struct radix_node **slots = node->slots, *slot;
	unsigned int height = node->height;
	int i, j, k;

	for (i = 0; i < RT_BRANCH_FACTOR; ++i) {
		slot = slots[i];
		if (slot) {
			if (height > 0) { // internal nodes
				radix_tree_dfs_dump (slot, prefix | (i << (RT_BRANCH_FACTOR_BIT * height)));
			} else { // leaf node, data node
				struct radix_data_node * dnode = (struct radix_data_node *) slot;
				prefix |= i;
				printf ("0x%lx->(0x%lx, %p)\n", prefix, dnode->key, dnode->data);
			}
		}
	}
}

void radix_tree_dump (struct radix_tree *tree) {
	struct radix_node * node, *slot, **slots;
	struct list_head rhead = LIST_HEAD_INIT (rhead);
	int i, empty;

	node = tree->root;
	radix_tree_dfs_dump (node, 0);
}
