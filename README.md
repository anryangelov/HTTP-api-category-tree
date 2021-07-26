# HTTP-api-category-tree
Backend HTTP-based API for a system to manage a category tree

add root category

    curl --header "Content-Type: application/json" \
    --request POST \
    --data '{"name":"B", "description":"B"}' \
    http://localhost:8000/category/
    
    {"category_id":8,"parent_category_id":null,"image":null,"name":"A","description":"A","similarities":[]}  
add image to the created category

    curl -F "image=@IMG_20200822_153113.jpg" \
     -X PUT http://127.0.0.1:8000/category/8/image/

    {"image":"/uploads/2021/07/23/IMG_20200822_153113.jpg"}

update category

    curl --header "Content-Type: application/json" \
     --request PUT \
     --data '{"name":"B", "description":"B", "parent_category_id":8}' \
     http://localhost:8000/category/9/

    {"category_id":9,"parent_category_id":null,"image":null,"name":"B","description":"B","similarities":[]}

add new root category with similarities

    curl --header "Content-Type: application/json" \
    --request POST \
    --data '{"name":"C", "description":"C", "similarities": [8]}' \
    http://localhost:8000/category/

    {"category_id":10,"parent_category_id":null,"image":null,"name":"C","description":"C","similarities":[8]}

PATCH http mehtod can be used for example to move category under another parent

    curl --header "Content-Type: application/json"      --request PATCH      --data '{"parent_category":10}'      http://localhost:8000/category/9/ | python -m         json.tool

    {
    "category_id": 9,
    "parent_category": 10,
    "image": null,
    "name": "B",
    "description": "B",
    "similarities": [
        11
    ]
    }


get children

    curl http://localhost:8000/category/8/children/?depth=2 | python -m json.tool


    [
    {
        "category_id": 8,
        "parent_category": null,
        "image": "/uploads/2021/07/23/IMG_20200822_153113.jpg",
        "name": "A",
        "description": "A",
        "similarities": [
            10,
            11
        ],
        "depth": 1
    },
    {
        "category_id": 9,
        "parent_category": 8,
        "image": null,
        "name": "B",
        "description": "B",
        "similarities": [
            11
        ],
        "depth": 2
    },
    {
        "category_id": 11,
        "parent_category": 8,
        "image": null,
        "name": "D",
        "description": "D",
        "similarities": [
            8,
            9,
            10
        ],
        "depth": 2
    }
    ]

get children nested as tree with tree query param
    
    curl "http://localhost:8000/category/8/children/?depth=2&tree=true" | python -m json.tool

    {
    "category_id": 8,
    "parent_category": null,
    "image": "/uploads/2021/07/23/IMG_20200822_153113.jpg",
    "name": "A",
    "description": "A",
    "similarities": [
        10,
        11
    ],
    "depth": 1,
    "children": [
        {
            "category_id": 10,
            "parent_category": 8,
            "image": null,
            "name": "C",
            "description": "C",
            "similarities": [
                8,
                11
            ],
            "depth": 2,
            "children": []
        },
        {
            "category_id": 11,
            "parent_category": 8,
            "image": "/uploads/2021/07/23/IMG_20200822_151252.jpg",
            "name": "D",
            "description": "D",
            "similarities": [
                8,
                9,
                10
            ],
            "depth": 2,
            "children": []
        }
    ]
    }


get parents

    curl http://localhost:8000/category/11/parents/ | python -m json.tool
    
    [
    {
        "category_id": 8,
        "parent_category": null,
        "image": "/uploads/2021/07/23/IMG_20200822_153113.jpg",
        "name": "A",
        "description": "A",
        "similarities": [
            10,
            11
        ],
        "depth": -1
    },
    {
        "category_id": 11,
        "parent_category": 8,
        "image": null,
        "name": "D",
        "description": "D",
        "similarities": [
            8,
            9,
            10
        ],
        "depth": 0
    }
    ]

get parent

    curl http://localhost:8000/category/11/parent/ | python -m json.tool

    {
    "category_id": 8,
    "parent_category": null,
    "image": "/uploads/2021/07/23/IMG_20200822_153113.jpg",
    "name": "A",
    "description": "A",
    "similarities": [
        10,
        11
    ]
    }
 

get rabbit islands through management command

    $ ./manage.py get_rabbit_islands
    ['A', 'B', 'C', 'D']
    ['G', 'M']

get longest rabbit hole

    $ ./manage.py get_longest_rabbit_hole
    ['C', 'D', 'B', 'W']
    ['A', 'D', 'B', 'W']

