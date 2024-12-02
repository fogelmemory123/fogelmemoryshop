async function addToCart(button) {
    const productId = button.getAttribute("data-id");
    const token = localStorage.getItem("access_token");
    if (!token) {
        alert("You need to log in to add items to the cart.");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:8000/api/cart/add/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
            },
            body: JSON.stringify({ product_id: productId, quantity: 1 }),
        });

        if (response.ok) {
            const result = await response.json();
            alert("Product added to cart!");
            await fetchCartSummary(); // Refresh the cart summary
        } else {
            const errorData = await response.json();
            alert(`Failed to add product to cart: ${errorData.detail || "Unknown error."}`);
        }
    } catch (error) {
        console.error("Error adding product to cart:", error);
        alert("An error occurred while adding the product to the cart.");
    }
}

async function fetchCartSummary() {
    const cartItemCount = document.getElementById("cart-item-count");
    const cartTotal = document.getElementById("cart-total");

    const token = localStorage.getItem("access_token");
    if (!token) {
        cartItemCount.textContent = "0";
        cartTotal.textContent = "0.00";
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:8000/api/cart/", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
            },
        });

        if (response.ok) {
            const cart = await response.json();
            let totalAmount = 0;

            cart.items.forEach((item) => {
                totalAmount += item.quantity * item.product.price;
            });

            cartItemCount.textContent = cart.items.length;
            cartTotal.textContent = totalAmount.toFixed(2);
        } else {
            console.error("Failed to fetch cart summary.");
            cartItemCount.textContent = "0";
            cartTotal.textContent = "0.00";
        }
    } catch (error) {
        console.error("Error fetching cart summary:", error);
        cartItemCount.textContent = "0";
        cartTotal.textContent = "0.00";
    }
}

async function fetchProducts() {
    const productsContainer = document.getElementById("products-container");
    const urlParams = new URLSearchParams(window.location.search);
    const amazonid = urlParams.get("id");
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/single-product/${amazonid}/`, {
            method: "GET",
            headers: { "Content-Type": "application/json" },
        });

        if (response.ok) {
            const products = await response.json();
            productsContainer.innerHTML = "";

            products.forEach((product) => {
                const productCard = `
                    <div class="col mb-5">
                        <div class="card h-100">
                            <img class="card-img-top" src="${product.image_url}" alt="${product.name}" />
                            <div class="card-body p-4">
                                <div class="text-center">
                                    <h5>
                                        <a href="product.html?id=${encodeURIComponent(product.description)}&product=${encodeURIComponent(product.id)}" class="text-decoration-none text-dark">
                                            ${product.name}
                                        </a>
                                    </h5>
                                    <p>$${product.price}</p>
                                </div>
                            </div>
                            <div class="card-footer p-4 pt-0 border-top-0 bg-transparent">
                                <div class="text-center">
                                    <button class="btn btn-outline-dark mt-auto" onclick="addToCart(this)" data-id="${product.id}">
                                        Add to Cart
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                productsContainer.innerHTML += productCard;
            });
        } else {
            console.error("Failed to fetch products");
        }
    } catch (error) {
        console.error("Error fetching products:", error);
    }
}

async function fetchUserInfo() {
    const userActions = document.getElementById("user-actions");
    const token = localStorage.getItem("access_token");

    if (!token) {
        userActions.innerHTML = `
            <a href="login.html" class="btn btn-outline-dark">Login</a>
        `;
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:8000/api/user-info/", {
            method: "GET",
            headers: { "Authorization": `Bearer ${token}` },
        });

        if (response.ok) {
            const data = await response.json();
            userActions.innerHTML = `
                <span>Welcome, <strong>${data.username}</strong></span>
                <button class="btn btn-outline-dark ms-2" onclick="logout()">Logout</button>
            `;
        } else {
            userActions.innerHTML = `<a href="login.html" class="btn btn-outline-dark">Login</a>`;
        }
    } catch (error) {
        console.error("Error fetching user info:", error);
        userActions.innerHTML = `<a href="login.html" class="btn btn-outline-dark">Login</a>`;
    }
}

function logout() {
    localStorage.removeItem("access_token");
    window.location.reload();
}

async function fetchCategories() {
    const categoryList = document.getElementById("categoryList");

    try {
        const response = await fetch("http://127.0.0.1:8000/api/categories/", {
            method: "GET",
            headers: { "Content-Type": "application/json" },
        });

        if (response.ok) {
            const categories = await response.json();
            categoryList.innerHTML = ""; // Clear existing categories

            categories.forEach((category) => {
                const categoryItem = `
                    <li><a class="dropdown-item" href="category.html?id=${category.id}">${category.name}</a></li>
                `;
                categoryList.innerHTML += categoryItem;
            });
        } else {
            console.error("Failed to fetch categories.");
        }
    } catch (error) {
        console.error("Error fetching categories:", error);
    }
}
function goToCartPage(){
    window.location.href="cart.html"
}
document.addEventListener("DOMContentLoaded", async () => {
    await fetchUserInfo();
    await fetchCartSummary();
    await fetchProducts();
    await fetchCategories();
});
