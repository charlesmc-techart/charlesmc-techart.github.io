SELECT category.category_name, skill.skill_name

FROM skl_categories AS category
         INNER JOIN skl_skills skill
                    ON skill.category_id = category.category_id

WHERE skill.skill_is_active IS TRUE

ORDER BY category.category_sort_index, skill.skill_sort_index,
         skill.skill_name;
