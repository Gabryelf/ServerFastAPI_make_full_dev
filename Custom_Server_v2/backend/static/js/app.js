class App {
    static init() {
        console.log('Marketplace app initialized');

        ProductsService.loadProducts();

        this.setupEventListeners();
    }

    static setupEventListeners() {
        document.getElementById('loginPassword').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                AuthService.login();
            }
        });

        document.getElementById('regPassword').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                AuthService.register();
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    App.init();
});