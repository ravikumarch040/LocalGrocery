import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import 'package:models/models.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../providers/api_providers.dart';
import '../../providers/products_provider.dart';
import '../../providers/store_provider.dart';

class ProductFormScreen extends ConsumerStatefulWidget {
  /// For edit: store product ID (from listStoreProducts). For add: null.
  final String? storeProductId;

  const ProductFormScreen({super.key, this.storeProductId});

  @override
  ConsumerState<ProductFormScreen> createState() => _ProductFormScreenState();
}

class _ProductFormScreenState extends ConsumerState<ProductFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _descController = TextEditingController();
  final _priceController = TextEditingController();
  final _stockController = TextEditingController();
  final _unitController = TextEditingController();
  final _imageUrlController = TextEditingController();
  final _barcodeController = TextEditingController();
  bool _isLoading = false;
  bool _isEdit = false;
  String? _categoryId;
  List<Category> _categories = [];
  bool _categoriesLoaded = false;
  String? _pickedImagePath;
  models.Product? _product; // set in edit mode when loading store product

  @override
  void initState() {
    super.initState();
    _isEdit = widget.storeProductId != null;
  }

  @override
  void dispose() {
    _nameController.dispose();
    _descController.dispose();
    _priceController.dispose();
    _stockController.dispose();
    _unitController.dispose();
    _imageUrlController.dispose();
    _barcodeController.dispose();
    super.dispose();
  }

  Future<void> _loadCategories() async {
    if (_categoriesLoaded) return;
    final catalog = ref.read(catalogServiceProvider);
    final res = await catalog.getCategories();
    if (res.success && res.data != null) {
      setState(() {
        _categories = res.data!;
        _categoriesLoaded = true;
        if (_categories.isNotEmpty && _categoryId == null) {
          _categoryId = _categories.first.id;
        }
      });
    }
  }

  Future<void> _loadStoreProduct() async {
    if (widget.storeProductId == null) return;
    final catalog = ref.read(catalogServiceProvider);
    final res = await catalog.getStoreProduct(widget.storeProductId!);
    if (res.success && res.data != null) {
      final sp = res.data!;
      final p = sp.product;
      if (p != null) {
        _nameController.text = p.name;
        _descController.text = p.description ?? '';
        _unitController.text = p.unit ?? '';
        _imageUrlController.text = p.imageUrl ?? '';
      }
      _priceController.text = (sp.storePrice ?? p?.basePrice ?? 0).toStringAsFixed(0);
      _stockController.text = sp.stockQuantity.toString();
      setState(() {
        _categoryId = p?.categoryId;
        _product = p;
      });
    }
  }

  Future<void> _pickImage() async {
    final picker = ImagePicker();
    final x = await picker.pickImage(source: ImageSource.gallery, maxWidth: 800, imageQuality: 85);
    if (x != null) setState(() => _pickedImagePath = x.path);
  }

  Future<void> _scanBarcode() async {
    final result = await context.push<String>('/inventory/barcode-scan');
    if (result != null && mounted) {
      _barcodeController.text = result;
      setState(() {});
    }
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isLoading = true);
    try {
      final catalog = ref.read(catalogServiceProvider);
      final store = await ref.read(retailerStoreProvider.future);
      if (store == null) {
        if (mounted) _showError('Store not found');
        return;
      }

      if (_isEdit && widget.storeProductId != null) {
        final stock = int.tryParse(_stockController.text.trim()) ?? 0;
        final price = double.tryParse(_priceController.text.trim()) ?? 0.0;
        final res = await catalog.updateStoreProduct(
          storeProductId: widget.storeProductId!,
          stockQuantity: stock,
          storePrice: price,
        );
        if (!mounted) return;
        if (!res.success) {
          _showError(res.message ?? 'Update failed');
          return;
        }
        final imageUrl = _imageUrlController.text.trim();
        if (_product != null && imageUrl.isNotEmpty) {
          await catalog.updateProduct(
            productId: _product!.id,
            imageUrl: imageUrl,
          );
        }
        if (!mounted) return;
        ref.invalidate(retailerStoreProductsProvider);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Product updated')),
        );
        context.pop();
      } else {
        final name = _nameController.text.trim();
        final description = _descController.text.trim().isEmpty ? null : _descController.text.trim();
        final basePrice = double.tryParse(_priceController.text.trim()) ?? 0.0;
        final stock = int.tryParse(_stockController.text.trim()) ?? 0;
        final unit = _unitController.text.trim().isEmpty ? null : _unitController.text.trim();
        if (_categoryId == null || _categoryId!.isEmpty) {
          _showError('Select a category');
          return;
        }
        final imageUrl = _imageUrlController.text.trim().isEmpty ? null : _imageUrlController.text.trim();
        final createRes = await catalog.createProduct(
          name: name,
          categoryId: _categoryId!,
          basePrice: basePrice,
          description: description,
          unit: unit,
          imageUrl: imageUrl,
        );
        if (!createRes.success || createRes.data == null) {
          if (mounted) _showError(createRes.message ?? 'Failed to create product');
          return;
        }
        final product = createRes.data!;
        final addRes = await catalog.addProductToStore(
          storeId: store.id,
          productId: product.id,
          stockQuantity: stock,
          storePrice: basePrice,
        );
        if (!mounted) return;
        if (addRes.success) {
          ref.invalidate(retailerStoreProductsProvider);
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Product added')),
          );
          context.pop();
        } else {
          _showError(addRes.message ?? 'Failed to add product to store');
        }
      }
    } catch (e) {
      if (mounted) _showError('Error: $e');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
  }

  Widget _buildImageSection() {
    final url = _imageUrlController.text.trim();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (_pickedImagePath != null && File(_pickedImagePath!).existsSync())
          Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: Image.file(
                File(_pickedImagePath!),
                height: 120,
                width: 120,
                fit: BoxFit.cover,
              ),
            ),
          )
        else if (url.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: CachedNetworkImage(
              imageUrl: url,
              height: 120,
              width: 120,
              fit: BoxFit.cover,
              placeholder: (_, __) => const SizedBox(
                height: 120,
                width: 120,
                child: Center(child: CircularProgressIndicator()),
              ),
              errorWidget: (_, __, ___) => const Icon(Icons.broken_image, size: 48),
            ),
          ),
        TextFormField(
          controller: _imageUrlController,
          decoration: const InputDecoration(
            labelText: 'Image URL (optional)',
            border: OutlineInputBorder(),
          ),
          keyboardType: TextInputType.url,
          onChanged: (_) => setState(() {}),
        ),
        const SizedBox(height: 8),
        OutlinedButton.icon(
          onPressed: _pickImage,
          icon: const Icon(Icons.add_photo_alternate),
          label: const Text('Pick photo from gallery'),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_isEdit ? 'Edit product' : 'Add product'),
      ),
      body: FutureBuilder<void>(
        future: _isEdit ? _loadStoreProduct() : _loadCategories(),
        builder: (context, snapshot) {
          if (_isEdit && snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (!_isEdit && !_categoriesLoaded) {
            return const Center(child: CircularProgressIndicator());
          }
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  TextFormField(
                    controller: _nameController,
                    readOnly: _isEdit,
                    decoration: const InputDecoration(
                      labelText: 'Product name',
                      border: OutlineInputBorder(),
                    ),
                    validator: (v) =>
                        (v == null || v.trim().isEmpty) ? 'Required' : null,
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _descController,
                    readOnly: _isEdit,
                    decoration: const InputDecoration(
                      labelText: 'Description',
                      border: OutlineInputBorder(),
                    ),
                    maxLines: 2,
                  ),
                  const SizedBox(height: 16),
                  _buildImageSection(),
                  if (!_isEdit) ...[
                    const SizedBox(height: 16),
                    DropdownButtonFormField<String>(
                      initialValue: _categoryId,
                      decoration: const InputDecoration(
                        labelText: 'Category',
                        border: OutlineInputBorder(),
                      ),
                      items: _categories
                          .map((c) => DropdownMenuItem(
                                value: c.id,
                                child: Text(c.name),
                              ))
                          .toList(),
                      onChanged: (v) => setState(() => _categoryId = v),
                      validator: (v) =>
                          (v == null || v.isEmpty) ? 'Required' : null,
                    ),
                  ],
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _priceController,
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      labelText: _isEdit ? 'Store price (₹)' : 'Price (₹)',
                      border: const OutlineInputBorder(),
                    ),
                    validator: (v) {
                      if (v == null || v.trim().isEmpty) return 'Required';
                      if (double.tryParse(v) == null) return 'Invalid number';
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _stockController,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: 'Stock',
                      border: OutlineInputBorder(),
                    ),
                    validator: (v) {
                      if (v == null || v.trim().isEmpty) return 'Required';
                      if (int.tryParse(v) == null) return 'Invalid number';
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _unitController,
                    readOnly: _isEdit,
                    decoration: const InputDecoration(
                      labelText: 'Unit (e.g. kg, pack)',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        flex: 2,
                        child: TextFormField(
                          controller: _barcodeController,
                          readOnly: _isEdit,
                          decoration: const InputDecoration(
                            labelText: 'Barcode / SKU (optional)',
                            border: OutlineInputBorder(),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      IconButton.filled(
                        onPressed: _isEdit ? null : _scanBarcode,
                        icon: const Icon(Icons.qr_code_scanner),
                        tooltip: 'Scan barcode',
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  FilledButton(
                    onPressed: _isLoading ? null : _save,
                    child: _isLoading
                        ? const SizedBox(
                            height: 24,
                            width: 24,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : Text(_isEdit ? 'Update' : 'Add product'),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
