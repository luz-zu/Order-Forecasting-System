window.onload = function () {
    // clear history
    if (window.history.replaceState) {
        window.history.replaceState(null, null, window.location.href);
    }

    
    // disable date
    // const orderDateInput = document.getElementById('ordered_date');
    // const deliveryDateInput = document.getElementById('delivery_date');

    // orderDateInput.addEventListener('change', function() {
    // const selectedOrderDate = new Date(orderDateInput.value);
    
    // const currentDate = new Date();

    // const minDeliveryDate = new Date(selectedOrderDate);
    // minDeliveryDate.setDate(selectedOrderDate.getDate() + 1);

    // deliveryDateInput.setAttribute('min', minDeliveryDate.toISOString().split('T')[0]);

    // deliveryDateInput.disabled = false;
    
    // if (selectedOrderDate < currentDate) {
    //     alert("Please select a valid future order date.");
    //     orderDateInput.value = '';
    //     deliveryDateInput.value = '';
    //     deliveryDateInput.disabled = true;
    // }
    // });


      // Hide messages after 10 seconds
  setTimeout(function() {
    var messagesContainer = document.querySelector('.messages');
    if (messagesContainer) {
        messagesContainer.style.display = 'none';
    }
}, 10000); // 10 seconds
    function toggleSidebar() {
        var sidebar = document.querySelector('.sidebar');
        sidebar.classList.toggle('hide-sidebar');
      }

    // category.html
    $('a[data-bs-toggle="modal"][data-bs-whatever="edit_category"]').on('click', function () {
        var currCategoryid = $(this).data('category-id');
        var currCategory = $(this).data('category-name');
        document.getElementById('category_id').value = currCategoryid;
        document.getElementById('old_category_name').value = currCategory;
    });

    // products.html
    $('a[data-bs-toggle="modal"][data-bs-whatever="edit_product"]').on('click', function () {
        var currProductID = $(this).data('product-id');
        var currProductName = $(this).data('product-name');
        var currProductDescription = $(this).data('product-description');
        document.getElementById('product_id').value = currProductID;
        document.getElementById('new_product_name').value = currProductName;
        document.getElementById('new_product_description').value = currProductDescription;
    });

    // order.html
    $('a[data-bs-toggle="modal"][data-bs-whatever="edit_order"]').on('click', function () {
        var currOrderId = $(this).data('order-id');
        var currProduct = $(this).data('product-name');
        var currQuantity = $(this).data('order-quantity');
        var currOrderPrice = $(this).data('order-price');
        var currDeliveryDate = new Date($(this).data('delivery-date')).toISOString().split('T')[0];
        var currOrderedDate = new Date($(this).data('ordered-date')).toISOString().split('T')[0];
        var currOrderStatus = $(this).data('order-status');
        document.getElementById('old_orderid').value = currOrderId;
        document.getElementById('new_product_name').value = currProduct;
        document.getElementById('edit_quantity').value = currQuantity;
        document.getElementById('edit_price').value = currOrderPrice;
        document.getElementById('edit_delivery_date').value = currDeliveryDate;
        document.getElementById('edit_ordered_date').value = currOrderedDate;
        document.getElementById('edit_status').value = currOrderStatus;
        
        console.log(currDeliveryDate);
    });

    // inventory.html
    $('a[data-bs-toggle="modal"][data-bs-whatever="edit_inventory"]').on('click', function () {
        var currInventoryId = $(this).data('inventory-id');
        var currProduct = $(this).data('product');
        var currQuantity = $(this).data('inventory-quantity');
        var currPrice = $(this).data('inventory-price');
        
        // Set values to the form fields
        document.getElementById('edit_inventory_id').value = currInventoryId;
        document.getElementById('product_dropdown').value = currProduct;
        document.getElementById('edit_quantity').value = currQuantity;
        document.getElementById('edit_price').value = currPrice;
        
        // Log for debugging
        console.log(currInventoryId, currProduct, currQuantity, currPrice);
    });
    
    


    // below code is to display the available category data in the dropdown menu
    $("#category_dropdown").on("click", function () {
        var categoryDropdown = $(this);

        if (categoryDropdown.children().length <= 1) {
            var categoryUrl = $("#category_url").val();

            $.ajax({
                url: categoryUrl,
                type: "GET",
                dataType: "json",
                success: function (data) {
                    categoryDropdown.empty();
                    categoryDropdown.append('<option value="">Select a category</option>');
                    $.each(data, function (index, category) {
                        categoryDropdown.append('<option value="' + category.category + '">' + category.category + '</option>');
                    });
                },
                error: function () {
                    console.log(data);
                }
            });
        }
    });

    $("#category_dropdown").on("change", function () {
        var selectedCategory = $(this).val();
        var productDropdown = $("#product_dropdown2");
    
        if (selectedCategory) {
            var productUrl = $("#product_url").val() + '?category=' + selectedCategory;
    
            $.ajax({
                url: productUrl,
                type: "GET",
                dataType: "json",
                success: function (data) {
                    productDropdown.empty();
                    productDropdown.append('<option value="">Select a product</option>');
                    $.each(data, function (index, product) {
                        productDropdown.append('<option value="' + product.product + '">' + product.product + '</option>');
                    });
                },
                error: function () {
                    console.log("Error fetching products.");
                }
            });
        } else {
            productDropdown.empty();
            productDropdown.append('<option value="">Select a product</option>');
        }
    });
    
    // This code disables the select category text after selecting the new data
    $("#category_dropdown").on("change", function () {
        var categoryDropdown = $(this);
        categoryDropdown.find("option[value='']").prop("disabled", true);
    });

    // fetch the product list
    $("#product_dropdown").on("click", function () {
        var product_dropdown = $(this);
        if (product_dropdown.children().length <= 1) {
            var productUrl = $("#product_url").val();

            $.ajax({
                url: productUrl,
                type: "GET",
                dataType: "json",
                success: function (data) {
                    product_dropdown.empty();
                    product_dropdown.append('<option value="">Select a product</option>');
                    $.each(data, function (index, product) {
                        product_dropdown.append('<option value="' + product.product_id + '">' + product.product + '</option>');
                    });
                },
                error: function () {
                    console.log(data);
                }
            });
        }
    });

    // Calender
    $('.datepicker').datepicker({
        format: 'yyyy-mm-dd',
        autoclose: true,
    });

    // This code disables the select product text after selecting the new data
    $("#product_dropdown").on("change", function () {
        var categoryDropdown = $(this);
        categoryDropdown.find("option[value='']").prop("disabled", true);
    });

    // Filter table
    $("#table-filter").on("keyup", function() {
        filterTable();
    });

    function filterTable() {
        var value = $("#table-filter").val().toLowerCase();

        $("table tbody tr").each(function() {
            var row = $(this);
            row.toggle(row.text().toLowerCase().indexOf(value) > -1);
        });
    };


    // monthly graph
    let xValues = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    let yValues = [7, 8, 8, 9, 9, 9, 10, 11, 14, 14, 15, 28];

    new Chart("monthly", {
        type: "line",
        data: {
            labels: xValues,
            datasets: [{
                fill: false,
                lineTension: 0,
                backgroundColor: "rgba(0,0,255,1.0)",
                borderColor: "rgba(0,0,255,0.1)",
                data: yValues
            }]
        },
        options: {
            legend: { display: false },
            scales: {
                yAxes: [{ ticks: { min: 1, max: 100 } }],
            }
        }
    });

    // Daily graph
    let x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31];
    let y = [7, 8, 8, 9, 9, 9, 10, 11, 14, 14, 15, 28];

    new Chart("daily", {
        type: "line",
        data: {
            labels: x,
            datasets: [{
                fill: false,
                lineTension: 0,
                backgroundColor: "rgba(0,0,255,1.0)",
                borderColor: "rgba(0,0,255,0.1)",
                data: y
            }]
        },
        options: {
            legend: { display: false },
            scales: {
                yAxes: [{ ticks: { min: 1, max: 100 } }],
            }
        }
    });
};

